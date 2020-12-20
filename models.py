#models 
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
db = SQLAlchemy() 



#association table to connect user and events many to many relationship
attending = db.Table('attending', 
    db.Column('attending_userid', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('attending_eventid', db.Integer, db.ForeignKey('events.event_id'))
)

#user 
class User(db.Model): 
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True) #standard primary key 
    username = db.Column(db.String(30), nullable=False, unique=True)  #unique username - cannot be blank
    password = db.Column(db.String(64), nullable=False) #password - hashed before saving to db & cannot be blank 
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    
    #user can host many events relationship 
    events_hosting = db.relationship('Event', foreign_keys=[event_id], backref='attendee')

    #user can attend many events, events can have many attendees
    attending = db.relationship('Event', secondary=attending, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    #need association table to associate primary key to a primary key in another table 
    def __init__(self, username, password):
        self.username = username
        self.password = password
        #self.event_id = event_id

    def __repr__(self):
	     return '<User {}>'.format(self.username)


 #user can attend many events & events will have many users attending 


#event 
class Event(db.Model): 
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False) #title column - cannot be blank 
    description = db.Column(db.String(400), nullable=True) #description column 
    start_dt = db.Column(db.DateTime, nullable=False) #start date & time column - cannot be blank 
    end_dt = db.Column(db.DateTime, nullable=False) #end date & time column - cannot be blank 
    user_id = db.Column(db.Integer, db.ForeignKey('users.username'))

    def __init__(self, title, description, start_dt, end_dt, user_id):
        self.title = title
        self.description = description 
        self.start_dt = start_dt
        self.end_dt = end_dt 
        self.user_id = user_id

    def __repr__(self):
	        return '<Event {}>'.format(self.title)
#relationship between user and event 
    #user can host many events 
    #user can attent many events & events will have many users attending 

#any additional columns 



	
