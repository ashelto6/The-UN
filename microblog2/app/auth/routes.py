from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route("/login", methods=['GET', 'POST'])
def login(): #always do data pre-checks for logins in the /login view function
    if current_user.is_authenticated: #if the user is already logged in...
        flash(_('You are already logged in'))
        return redirect(url_for('main.index')) #direct to home page
    form = LoginForm() #if user is not already logged in, form is set as an instance of class LoginForm   
    if form.validate_on_submit(): #if the user submits the form
        user = User.query.filter_by(username=form.username.data.lower()).first() #assigns user to matching username or None if username doesn't exist in database
        if user is None or not user.check_password(form.password.data): #user.check_password checks the encrypted password for a match #if username is =None or password is no match, continue into body, if not, move on to login_user instance
            flash(_('Invalid username or password')) #prints a message to user
            return redirect(url_for('auth.login')) #if user or password is wrong, reload login page
        login_user(user, remember=form.remember_me.data) #if login credentials correct, logs the user in
        next_page = request.args.get('next') #next_page contains the 'next' link which is used to direct the user back to their previous page after logging in
        if not next_page or url_parse(next_page).netloc != '': #if a 'next' extension doesnt exist, or it contains an unrelevant link continue, otherwise, skip to return statement
            next_page = url_for('main.index') #reassigns next_page the url to the home page
        flash(_('Welcome, %(current_user)s!', current_user=current_user.username.title()))    
        return redirect(next_page) #redirect to next_page
    return render_template('auth/login.html', title=_('Sign In'), form=form) #colored 'form' contains all the user's form data, 'form' can be accessed by 'login.html' to print data to the page usually using the "." operator

@bp.route('/logout')
def logout():
    logout_user() #logs user out of application
    return redirect(url_for('auth.login')) #redirects to login page

@bp.route('/register', methods=['GET', 'POST']) 
def register(): #data pre-checks are done in forms.py, so the form can check the inputs for invalidity and inform the user of the invalidity before the page can be submitted
    if current_user.is_authenticated: #if the user is already logged in
        flash(_('You are already a registered user'))
        return redirect(url_for('main.index')) #redirects to homepage IF user is authenticated
    form = RegistrationForm() #if user not logged in, form is set to an instance of RegistrationForm class
    if form.validate_on_submit(): #if the user submitted the form
        user=User(username=form.username.data.lower(), email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data) # assigns 'user' the data (username and email) that was submitted to the form by the user
        user.set_password(form.password.data) # uses the password given in the registration form, assigns it to the user variable
        db.session.add(user) #adds the user and their credentials to the data base
        db.session.commit() #applys changes to the data base
        flash(_('Congratulations, You are now a registered user!')) #print's confirmation message to user
        return redirect(url_for('auth.login')) #redirects user to login page after registration is complete
    
    return render_template('auth/register.html', title=_('Register'), form=form) #colored 'form' contains all the user's form data, 'form' can be accessed by 'register.html' to print data to the page usually using the "." operator

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        flash(_('You can not do a password reset while logged in'))
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None:
            send_password_reset_email(user)
        flash(_('Check your email for instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title = _('Reset Password Request'), form = form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash(_('You must access this page via email link'))
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title = _('Reset Password'), form=form)    