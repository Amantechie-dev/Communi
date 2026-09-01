from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'hackathon_mvp_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///communi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    organizer_email = db.Column(db.String(100), nullable=False) 
    hours = db.Column(db.Integer, nullable=False, default=1)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()



@app.route('/')
def home():
    
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            new_user = User(name=email.split('@')[0], email=email)
            db.session.add(new_user)
            db.session.commit()
        
        
        session['logged_in_user'] = email
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in_user', None)
    return redirect(url_for('home'))


@app.route('/create', methods=['GET', 'POST'])
def create_event():
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        hours = int(request.form['hours']) 
        organizer = session['logged_in_user']
        
        
        new_event = Event(title=title, description=description, location=location, hours=hours, organizer_email=organizer)
        db.session.add(new_event)
        db.session.commit()
        
        return redirect(url_for('explore'))
        
    return render_template('create.html')


@app.route('/explore')
def explore():
    
    all_events = Event.query.all()
    return render_template('explore.html', events=all_events)


@app.route('/join/<int:event_id>')
def join_event(event_id):
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))
        
    user_email = session['logged_in_user']
    
    
    existing = Attendance.query.filter_by(user_email=user_email, event_id=event_id).first()
    if not existing:
        new_attendance = Attendance(user_email=user_email, event_id=event_id)
        db.session.add(new_attendance)
        db.session.commit()
        
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))
        
    user_email = session['logged_in_user']
    
    
    my_events = Event.query.filter_by(organizer_email=user_email).all()
    
    
    my_attendances = Attendance.query.filter_by(user_email=user_email).all()
    joined_event_ids = [a.event_id for a in my_attendances]
    joined_events = Event.query.filter(Event.id.in_(joined_event_ids)).all()
    total_hours = sum(event.hours for event in joined_events)
    return render_template('dashboard.html', my_events=my_events, joined_events=joined_events,total_hours=total_hours)

if __name__ == '__main__':
    app.run(debug=True)