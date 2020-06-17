from hashlib import md5
from app import login, db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
from flask import current_app
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
  @classmethod
  def search(cls, expression, page, per_page):
    ids, total = query_index(cls.__tablename__, expression, page, per_page)
    if total == 0:
      return cls.query.filter_by(id=0), 0 
    when = []
    for i in range(len(ids)):
      when.append((ids[i], i))
    return cls.query.filter(cls.id.in_(ids)).order_by(
      db.case(when, value=cls.id)), total

  @classmethod
  def before_commit(cls, session):
    session._changes = {
      'add': list(session.new),
      'update': list(session.dirty),
      'delete': list(session.deleted)
    }

  @classmethod
  def after_commit(cls, session):
    for obj in session._changes['add']:
      if isinstance(obj, SearchableMixin):
        add_to_index(obj.__tablename__, obj)
    for obj in session._changes['update']:
      if isinstance(obj, SearchableMixin):
        add_to_index(obj.__tablename__, obj)
    for obj in session._changes['delete']:
      if isinstance(obj, SearchableMixin):
        remove_from_index(obj.__tablename__, obj)
    session._changes = None

  @classmethod
  def reindex(cls):
    for obj in cls.query:
      add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

followers = db.Table('followers', #follower system association table
  db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), 
  db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
  )

class User(UserMixin, db.Model): #database model for Users
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)  
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  posts = db.relationship('Post', backref='author', lazy='dynamic')
  about_me = db.Column(db.String(140)) 
  last_seen = db.Column(db.DateTime, default=datetime.utcnow)
  followed = db.relationship(
    'User', secondary = followers, 
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id==id),
    backref=db.backref('followers', lazy = 'dynamic'), lazy='dynamic' ) 


  def __repr__(self): #method defines the format in which the data is displayed returns <User: (self.username value)>
    return '<User ID: {}, FN: {}, LN: {}, Username: {}, Email: {}, LS: {}>\n'.format(self.id, self.first_name, self.last_name, self.username, self.email, self.last_seen)
  
  def set_password(self, password): #method for generating password hash
    self.password_hash = generate_password_hash(password)

  def check_password(self, password): #method for password verification
    return check_password_hash(self.password_hash, password)

  def avatar(self, size): #method that handles avatar loading
    digest = md5(self.email.lower().encode('utf-8')).hexdigest() #ecodes user's lowercase email into bits so it is understandable to hex
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size) #returns avatar image link for 'self' user
  
  def follow(self, user):
    if not self.is_following(user): #if follower user doesnt already follow the user... 
      self.followed.append(user) #follower user follows the user

  def unfollow(self, user):
    if self.is_following(user): #if follower user already follows the user...
      self.followed.remove(user) #follower user unfollows the user

  def is_following(self, user): #checks is users follow each other already or not
    return self.followed.filter(
      followers.c.followed_id == user.id).count() > 0 #issues a query on the followed relationship to check if a link between two users already exist. followers.c.followed_id == user.id looks for items in the association table that have the left side foreign key set to the 'self' user and the right side set to the 'user' argument. The query is terminated with a count() method, which will return 1 if a match is found and 0 if no matches found.

  def followed_posts(self): #returns the posts by the current user and the users he/she follows ONLY ordered newest to oldest 
    followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id) 
  #the first argument of join() is the followers association table located at the beginning of this file, the second argument is the join conditional. with this call, the db will create a temp table that combines data from posts and followers tables. Only data that match the condition will be added to the temp table. The condition that I used says that the followed_id field of the followers table must be equal to the user_id of the posts table to be added to temp db. The db takes each record from the posts table and any records from the followers table that match the condition and appends them to the temp db. If for a given post there is no match in followers, then that post record is not part of the join. the .filter call ensures that we only get posts from users that are followed by the user in question
    own = Post.query.filter_by(user_id=self.id)
    return followed.union(own).order_by(Post.timestamp.desc()) #union combines the 'followed' posts query results and the current user's 'own' posts query results and returns all of the posts in order newest to oldest

  def get_reset_password_token(self, expires_in=600): #method generates an encoded token that is valid for up to 10 minutes
    return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

  @staticmethod
  def verify_reset_password_token(token): #verifies that the token is valid
    try: 
      id = jwt.decode(token, current_app.config['SECRET_KEY'], #if the token is valid, it is decoded and the user's info, kept inside of the 'reset password' key is set to the 'id' variable
      algorithms=['HS256'])['reset_password']

    except: #if token is not valid...
      return #return None
    return User.query.get(id) #if the token is decoded and verified successfully we return the user found in our database

@login.user_loader #decorator registers function with Flask-Login
def load_user(id):
  return User.query.get(int(id))

class Post(SearchableMixin, db.Model): #database model for Posts
  __searchable__ = ['body']
  id = db.Column(db.Integer, primary_key = True)
  body = db.Column(db.String(140), index = True)
  timestamp =db.Column(db.DateTime, index=True, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #user.id is a foreign key that connects the Post table with the User table
  language = db.Column('language', db.String(length=5), nullable=True)

  def __repr__(self): #method defines the format in which the data is displayed returns <Post: (self.body value)>
    return '<UserID: {}, PostID: {}, Post: {}, PostTime: {}>\n'.format(self.user_id, self.id, self.body, self.timestamp)