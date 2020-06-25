import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
 SECRET_KEY = os.environ.get('SECRET KEY') or 'you-will-never-guess'
 SQLALCHEMY_DATABASE_URI =os.environ.get('DATABASE_URL') or \
  'sqlite:///' + os.path.join(basedir, "app.db")
 SQLALCHEMY_TRACK_MODIFICATIONS = False
 
 #configuring flask to send emails for errors, using the following configuration variables
 MAIL_SERVER = os.environ.get('MAIL_SERVER') #arguments are environment variables of os, their values are assigned to the instance variable on the LHS of =
 MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
 MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None #boolean, used to enable encrypted connections
 MAIL_USERNAME = os.environ.get('MAIL_USERNAME') #optional, a username does not have to exist
 MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') #optional, a password does not have to exists
 ADMINS = ['ashelto6@kent.edu'] #what emails receive error reports
 POSTS_PER_PAGE=5 #number of posts seen per page
 LANGUAGES = ['en', 'es']
 ELASTICSEARCH_URL =os.environ.get('ELASTICSEARCH_URL')
 MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
 NEW_USER_MESSAGE = 'Thank you for signing up! I am the site Admin & Developer! I have already went ahead and followed you, now I can see all of your great posts in my home feed!'