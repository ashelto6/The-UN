from app import db
from app.forms import RegistrationForm
from app import app
from flask import render_template, flash, redirect
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from flask import url_for
from datetime import datetime
from app.forms import EditProfileForm


# the syntax {some data: variable} is a dictionary

@app.route("/")  # decorator
@app.route("/index")  # decorator
@login_required
def index():  # view function
    user = {"username": "Tony"} # this is a 1 key dictionary
    posts = [ # posts is a list of dictionaries that each has 2 keys, "author" and "body". the "author" key gets its value from a 1 key dictionary
        {"author": {"username": "John"}, "body": "Beautiful day in Kent!"},
        {"author": {"username": "Susan"}, "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut luctus consequat tortor, nec lacinia urna porta vitae. Curabitur id neque odio. Sed dui elit, vehicula nec ex ac, vestibulum varius erat. Nullam eleifend pharetra scelerisque. Mauris condimentum, elit vel suscipit interdum, dolor arcu vulputate odio, vel tempor tortor enim quis nisi. Ut vestibulum elit tortor, et eleifend sapien malesuada ut. Ut quis imperdiet erat, ac egestas nibh. Vestibulum at mauris diam. Nam id ultrices tellus, sit amet commodo magna."},
    ]
    return render_template("index.html", title="Home Page", posts=posts) # function returns above values to the given html file

# 'GET' & 'POST' accepts user data from the site form
@app.route("/login", methods=['GET', 'POST']) 
def login():
    if current_user.is_authenticated: 
        return redirect(url_for('index')) # if user is logged in already, direct to home page
    form = LoginForm() #if not logged in, form is set as an instance of class LoginForm   
    if form.validate_on_submit(): #if not logged in, process the form data
        user = User.query.filter_by(username=form.username.data).first() #assigns user to matching username or None if username doesn't exist in database
        if user is None or not user.check_password(form.password.data): #user.check_password checks the encrypted password #if username is =None or password is incorrect, continue, if not, move on to logon_user instance
            flash('Invalid username or password') #flash() = print() but illegal with flask
            return redirect(url_for('login')) #if user or password is wrong, reload login page
        login_user(user, remember=form.remember_me.data) #if login credentials correct, logs the user in
        next_page = request.args.get('next') #next_page contains the 'next' link which directs the user back to their previous page after logging in
        if not next_page or url_parse(next_page).netloc != '': #if a 'next' extension doesnt exist, or it contains an unrelevant link continue, otherwise, skip to return statement
            next_page = url_for('index') #reassigns next_page the url to the home page
        return redirect(next_page) #redirect to next_page
    return render_template('login.html', title='Sign In', form=form) #renders definition in html

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('index')) #redirects to homepage IF user is authenticated
    form = RegistrationForm() #if user not authenticated, form is set to an instance of RegistrationForm class
    if form.validate_on_submit(): #checks the user data
        user=User(username=form.username.data, email=form.email.data) # assigns 'user' the data (username and email) that was submitted to the form by the user
        user.set_password(form.password.data) # uses the password given in the registration form, assigns it to the user variable
        db.session.add(user) #adds the user and their credentials to the data base
        db.session.commit() #applys changes to the data base
        flash('Congratulations, You are now a registered user!') #print's confirmation message to user
        return redirect(url_for('login')) #redirects user to login page after registration is complete
    
    return render_template('register.html', title='Register', form=form)
    
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)