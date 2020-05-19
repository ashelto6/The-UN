from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)  # object variable that's assigned an instance of class Flask
app.config.from_object(Config)
db = SQLAlchemy(app) #object variable that contains an instance of SQLAlchemy class that takes our application package as an argument
migrate = Migrate(app, db) 
login = LoginManager(app)
login.login_view = 'login'


from app import routes, models
