from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class EditProfileForm(FlaskForm): #form for user profile modification
  username = StringField(_l('Username'), validators=[DataRequired()])
  about_me = TextAreaField(_l('Bio'), validators=[Length(min=0, max=140)])
  submit = SubmitField(_l('Save'))

  def __init__(self, original_username, *args, **kwargs): #custom validation method, invoked implicitly
    super(EditProfileForm, self).__init__(*args, **kwargs) #an overloaded constructor 
    self.original_username = original_username #the user's current username(at that given time) is set to the self.original_username instance variable

  def validate_username(self, username): #checks if the username is available, invoked once user attep=mps to submit
    if username.data.lower() != self.original_username: #if original_username is != the named submitted to replace original_username, execute the body of if statement, if original_username == the replacement name, skip body of if statement
      user = User.query.filter_by(username=self.username.data.lower()).first() #checks if the replacement username is already in the database, if so, the matching username is set to the user variable. if the replacement username is not in the db user is set to 'None' 
      if user is not None: #if user == a value other than 'None', execute body of if statement. if user == 'None' skip the body of if statement
        raise ValidationError(_('That username is taken. Please choose a different username'))

class EmptyForm(FlaskForm): # form used as follow and unfollow button
  submit = SubmitField(_l('Submit'))

class SearchForm(FlaskForm):
  q = StringField(_l('Username / Post Keywords'), validators = [DataRequired()])

  def __init__(self, *args, **kwargs):
    if 'formdata' not in kwargs:
      kwargs['formdata'] = request.args
    if 'csrf_enabled' not in kwargs:
      kwargs['csrf_enabled'] = False
    super(SearchForm, self).__init__(*args, **kwargs)
    
class CloseAccountForm(FlaskForm):
  submit = SubmitField(_l('Close Account'))

class DeletePostForm(FlaskForm):
  submit = SubmitField(_l('Delete Post'))

class UpdatePostForm(FlaskForm):
  post = TextAreaField(validators=[DataRequired(), Length(min=1, max=240)])
  submit = SubmitField(_l('Update Post'))

class PostForm(FlaskForm): #form used for blog posts
  post = TextAreaField(_l('What would you like to share?'), validators=[DataRequired(), Length(min=1, max=240)])
  submit = SubmitField(_l('Post'))

class MessageForm(FlaskForm):
  message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min = 0, max = 140)])
  submit = SubmitField(_l('Send'))