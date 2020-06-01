from threading import Thread
from flask_mail import Message
from app import mail
from flask import current_app

def send_async_email(app, msg): #allows for emails to be sent in background while server is running
  with app.app_context():
    mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body): #helper function, creates and sends email
  msg = Message(subject, sender=sender, recipients=recipients)
  msg.body = text_body
  msg.html = html_body
  Thread(target=send_async_email, args=(current_app._get_current_object(),msg)).start() #begins the background sending of emails



