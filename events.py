#controller
import time 
from datetime import datetime
import os
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack 
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Event


app = Flask(__name__) 

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default',

	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'events.db')
))
app.config.from_envvar('EVENTS_SETTINGS', silent=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning


db.init_app(app) #initialize the database 

#initializes the database via the command line
@app.cli.command('initdb')
def initdb_command():
	db.create_all()
	print('Initialized the database! Good to go.')

#next three are helper methods 
def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None #return the user id if the user was returned in rv or else it will return in none 


#make a date time object and print it out in the format that we want 
def format_datetime(start_datetime):
	"""Format a timestamp for display."""
	return (start_datetime).strftime('%Y-%m-%d @ %H:%M')

#that g that we imported above is a variable that exists within the application scope 
#g gives us a global location within all of our functions to store information 
#global data DURING request, not during sessions
@app.before_request
def before_request():
	g.user = None #create user and set it to none 
	if 'user_id' in session: #is the user logged in? 
		g.user = User.query.filter_by(user_id=session['user_id']).first()
		#pull the user who is logged in and put it in g.user 

@app.route('/')
def timeline(): 
    return redirect(url_for('homepage'))

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if g.user: #if the user is logged in.. send them to homepage
        return redirect(url_for('homepage'))
    error = None #track error 
    if request.method == 'POST': #you want to send something to the server
        user = User.query.filter_by(username=request.form['username']).first() #get their username
        if user is None: #if it doesn't match any in the database 
            error = 'Invalid username' 
        elif not check_password_hash(user.password, request.form['password']): #check their password
            error = 'Invalid password' #doesn't match 
        else: 
            flash('You were logged in')
            session['user_id']=user.user_id #log them in
            return redirect(url_for('homepage')) #send them to the home page
    return render_template('login.html', error=error) #print their error 
    
@app.route('/registration', methods=['GET', 'POST'])
def register():
	if g.user: #if user is logged in, go to their timeline 
		return redirect(url_for('homepage'))
	error = None #keep track of error 
	if request.method == 'POST':
		if not request.form['username']: #if the user didn't enter a username
			error = 'You did not enter a username, enter one to register!'
		elif not request.form['password']: #if the user didn't enter a password
			error = 'You did not enter a password, enter one to register!'
		elif get_user_id(request.form['username']) is not None: #if the username is already taken
			error = 'The username is already taken'
		else:
            #add the user, email, and hashed password into the database
			db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
			db.session.commit() #commit to data base
			flash('Successfully registered, now log in!')
			return redirect(url_for('login')) #send them to the login page 
	return render_template('registration.html', error=error) #if everything else failed, print their error


@app.route('/register_to_attend', methods=['GET', 'POST'])
def register_to_attend():
	if g.user: #if user is logged in, go to their timeline 
		return redirect(url_for('homepage'))
	error = None #keep track of error 
	if request.method == 'POST':
		if not request.form['username']: #if the user didn't enter a username
			error = 'You did not enter a username, enter one to register!'
		elif not request.form['password']: #if the user didn't enter a password
			error = 'You did not enter a password, enter one to register!'
		elif get_user_id(request.form['username']) is not None: #if the username is already taken
			error = 'The username is already taken'
		else:
            #add the user, email, and hashed password into the database
			db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
			db.session.commit() #commit to data base
			flash('Successfully registered, now log in!')
			return redirect(url_for('login')) #send them to the login page 
	return render_template('registration.html', error=error) #if everything else failed, print their error


@app.route('/logout')
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.pop('user_id', None) #make them log out as far as the server is concerned 
	return redirect(url_for('homepage'))


@app.route('/homepage')
def homepage():
	if g.user: 
		myevents= Event.query.filter(Event.user_id == g.user.username).order_by(Event.start_dt)
		events = Event.query.order_by(Event.start_dt)
		att = User.query.filter_by(user_id=session['user_id']).first().attending.order_by(Event.start_dt)
		return render_template('homepage.html', events=events, myevents=myevents, att=att)
	else: 
		no_register_event = Event.query.order_by(Event.start_dt)
		return render_template('homepage.html', no_register_event=no_register_event)
	

#EVENT route to create an event with the logged in user as a host 
@app.route('/eventcreation', methods=['GET', 'POST'])
def eventcreation(): 
	if not g.user: abort(401)
	error = None #Track error
	if request.method == 'POST':
		if not request.form['title']: 
			error = "You did not enter a title, try again"
		elif not request.form['start']:
			error = "You did not enter a start date & time, try again"
		elif not request.form['end']:
			error = "You did not enter a end date & time, try again"
		else:
			start_datetime = datetime.fromisoformat(request.form['start'])
			end_datetime = datetime.fromisoformat(request.form['end'])
			new = Event(request.form['title'], request.form['description'], start_datetime, end_datetime, g.user.username)
			db.session.add(new) #add to session
			db.session.commit() #commit to database 
			flash('New entry was successfully posted')
	return render_template('eventcreation.html', error=error)

@app.route('/eventcancel/eventcancellation/<event_id>', methods=['GET', 'POST'])
def eventcancellation(event_id): 
	#go to other cancelation page and have a form that says are you sure you want to cancel? 
	event = Event.query.filter(Event.event_id == event_id).first()
	db.session.delete(event)
	flash("Your event was deleted!")
	db.session.commit()
	return redirect(url_for('homepage'))

@app.route('/eventcancel/<event_id>', methods=['GET', 'POST'])
def eventcancel(event_id): 
	event = Event.query.filter(Event.event_id == event_id).first()
	return render_template('eventcancellation.html', event=event)

@app.route('/registration/<event_id>', methods=['GET', 'POST'])
def registration(event_id): 
	attending_eventid = Event.query.filter(Event.event_id == event_id).first()
	User.query.filter_by(user_id=session['user_id']).first().attending.append(attending_eventid)
	db.session.commit() #save that information back to the database 
	flash('You are now registered for event: "%s"' % attending_eventid.title)
	return redirect(url_for('homepage'))

app.jinja_env.filters['datetimeformat'] = format_datetime 