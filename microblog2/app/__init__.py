from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask import request, current_app
from elasticsearch import Elasticsearch

#creating instances of imports

db = SQLAlchemy() 
migrate = Migrate() 
login = LoginManager()
login.login_view = 'auth.login'
login.login_message=_l('Please log in to view this page.')
bootstrap=Bootstrap()
moment = Moment()
babel = Babel()
mail=Mail()

def create_app(config_class=Config):
  app = Flask(__name__)  
  app.config.from_object(Config)
  db.init_app(app)
  migrate.init_app(app, db)
  login.init_app(app)
  bootstrap.init_app(app)
  moment.init_app(app)
  babel.init_app(app)
  mail.init_app(app)
  app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None

  from app.errors import bp as errors_bp
  app.register_blueprint(errors_bp)

  from app.auth import bp as auth_bp
  app.register_blueprint(auth_bp, url_prefix='/auth')

  from app.main import bp as main_bp
  app.register_blueprint(main_bp)

  #setting error-report email server
  if not app.debug and not app.testing: #if application is not in debug mode..
    if app.config['MAIL_SERVER']: #if a Mail Server exists...
      auth = None
      if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']: #if a Mail server username and password exists..
        auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
      secure = None
      if app.config['MAIL_USE_TLS']: #if MAIL_USE_TLS exists...
        secure = ()
      mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']), 
        fromaddr = 'no-reply@' + app.config['MAIL_SERVER'], toaddrs = app.config['ADMINS'], subject='Development Error Found', 
        credentials=auth,secure=secure) #setting the mail_handler instance variable to an instance of the SMTPHandler class with our server info
      mail_handler.setLevel(logging.ERROR) #emails will contain 'ERROR' level reports ONLY
      app.logger.addHandler(mail_handler) #adds mail_handler to app logger

  #writing error data to a file
    if not os.path.exists('logs'): #if no logs directory exists...
      os.mkdir('logs') #create a logs directory
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10) #setting max size of error-report file, and max amount of files that will be remembered at a time
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')) #setting the info we want in the error-report file
    file_handler.setLevel(logging.INFO) #declaring we want the handler to report with 'INFO' level information (gives more info than 'ERROR' level)
    app.logger.addHandler(file_handler) #adds filehandler to app logger
    app.logger.setLevel(logging.INFO) #declaring we want the app logger to report with 'INFO' level information
    app.logger.info('Microblog Startup') #writes this message to logs each time the server starts

  return app

@babel.localeselector
def get_locale():
  return request.accept_languages.best_match(current_app.config['LANGUAGES'])
  #return 'es'

from app import models
