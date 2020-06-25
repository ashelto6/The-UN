from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User

class LoginForm(FlaskForm): #login form field template, [DataRequired()] indicates a required field within the form
  username = StringField(_l('Username'), validators = [DataRequired()]) #first argument of class, labels the form field (has no other use), second argument requires some data for submission
  password = PasswordField(_l('Password'), validators = [DataRequired()])
  remember_me = BooleanField(_l('This is my personal device'))
  submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm): #form for user registration fields,
  first_name = StringField(_l('First Name'), validators=[DataRequired()])
  last_name = StringField(_l('Last Name'), validators=[DataRequired()])      
  username = StringField(_l('Username'), validators=[DataRequired()])
  email = StringField(_l('Email'), validators=[DataRequired(), Email()])
  password = PasswordField(_l('Password'), validators=[DataRequired()])
  password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')]) #EqualTo() indicates that the field must match it's argument's value
  submit = SubmitField(_l('Register')) 

  def validate_username(self, username): #custom validator checks the database to make sure no usernames match the form input
    user = User.query.filter_by(username=username.data.lower()).first()
    if user is not None: #if a matching email is found in the db, print the raise statement
      raise ValidationError(_('That username is taken. Please choose a different username')) 

  def validate_email(self, email): #checks the database to make sure no emails match the form input
    user=User.query.filter_by(email=email.data).first() #user is set == to 'None' ONLY if matching email not found in db, if match found, user == matching email
    if user is not None: #if a match is found, print the raise statement
      raise ValidationError(_('That email is taken. Please choose a different email'))

class ResetPasswordRequestForm(FlaskForm): #form for requesting a password reset link
  email = StringField(_l('Enter the email associated with your account'), validators=[DataRequired(), Email()])
  submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm): #form for once reset link is clicked and validated
  password = PasswordField(_l('New Password') , validators=[DataRequired()])
  password2 = PasswordField(_l('Repeat New Password'), validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField(_l('Request Password Reset'))
  