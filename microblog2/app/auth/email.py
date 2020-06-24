from flask import render_template, current_app
from flask_babel import _
from app.email import send_email

def send_password_reset_email(user):
  token = user.get_reset_password_token() #token is set to a generated encrypted token which will be used in the reset password email link
  send_email(_('Reset Your Password'), sender=current_app.config['ADMINS'][0], #sets the info needed to send emails
  recipients=[user.email], text_body = render_template('email/reset_password.txt',
  user=user, token=token),
  html_body=render_template('email/reset_password.html', user=user, token=token))