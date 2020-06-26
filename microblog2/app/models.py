from hashlib import md5
from app import login, db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
from flask import current_app
from app.search import add_to_index, remove_from_index, query_index
from flask import url_for
import json
import base64
import os

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

class PaginatedAPIMixin(object):
  @staticmethod
  def to_collection_dict(query, page, per_page, endpoint, **kwargs):
    resources = query.paginate(page, per_page, False)
    data = {
      'items': [item.to_dict() for item in resources.items],
      '_meta': {
        'page' : page,
        'per_page': per_page,
        'total_pages': resources.pages,
        'total_items': resources.total
      },
      '_links': {
        'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
        'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if resources.has_next else None,
        'prev': url_for(endpoint, page=page -1, per_page=per_page, **kwargs) if resources.has_prev else None 
      }
    }
    return data

class User(PaginatedAPIMixin, UserMixin, db.Model): #database model for Users
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
  messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='author', lazy='dynamic')
  messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref = 'recipient', lazy='dynamic')
  last_message_read_time = db.Column(db.DateTime)
  notifications = db.relationship('Notification', backref='user', lazy='dynamic')
  token = db.Column(db.String(32), index=True, unique=True)
  token_expiration = db.Column(db.DateTime)

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

  def followed_posts(self): #returns the posts by the current user and the users he/she follows ONLY, ordered newest to oldest 
    followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id) 
  #the first argument of join() is the followers association table located at the beginning of this file, the second argument is the join conditional. with this call, the db will create a temp table that combines data from posts and followers tables. Only data that match the condition will be added to the temp table. The condition that I used says that the followed_id field of the followers table must be equal to the user_id of the posts table to be added to temp db. The db takes each record from the posts table and any records from the followers table that match the condition and appends them to the temp db. If for a given post there is no match in followers, then that post record is not part of the join. the .filter call ensures that we only get posts from users that are followed by the current user
    own = Post.query.filter_by(user_id=self.id)
    return followed.union(own).order_by(Post.timestamp.desc()) #union combines the 'followed' posts query results and the current user's 'own' posts query results and returns all of the posts in order newest to oldest

  def get_reset_password_token(self, expires_in=600): #method generates an encoded token that is valid for up to 10 minutes
    return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
  
  def new_messages(self):
    last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
    return Message.query.filter_by(recipient=self).filter(
      Message.timestamp > last_read_time).count()
  
  def add_notification(self, name, data):
    self.notifications.filter_by(name=name).delete()
    n = Notification(name=name, payload_json = json.dumps(data), user=self)
    db.session.add(n)
    return n

  def to_dict(self, include_email=False):
    data = {
      'id': self.id,
      'username' : self.username,
      'last_seen': self.last_seen.isoformat() + 'Z',
      'about_me': self.about_me,
      'post_count': self.posts.count(),
      'followers_count': self.followers.count(),
      'followed_count': self.followed.count(),
      '_links': {
        'self': url_for('api.get_user', id=self.id),
        'followers': url_for('api.get_followers', id=self.id),
        'followed': url_for('api.get_followed', id=self.id),
        'avatar': self.avatar(128)
      }
    }
          
    if include_email:
      data['email'] = self.email
    return data
  
  def from_dict(self, data, new_user=False):
    for field in ['username', 'email', 'about_me']:
      if field in data:
        setattr(self, field, data[field])
    if new_user and 'password' in data:
      self.set_password(data['password'])

  def get_token(self, expires_in=3600):
    now = datetime.utcnow()
    if self.token and self.token_expiration > now + timedelta(seconds=60):
      return self.token
    self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
    self.token_expiration = now + timedelta(seconds=expires_in)
    db.session.add(self)
    return self.token

  def revoke_token(self):
    self.token_expiration = datetime.utcnow() - timedelta(seconds=1)


  @staticmethod
  def check_token(token):
    user = User.query.filter_by(token=token).first()
    if user is None or user.token_expiration < datetime.utcnow():
      return None
    return user
    
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

class Notification(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), index=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  timestamp = db.Column(db.Float, index=True, default=time)
  payload_json = db.Column(db.Text)

  def get_data(self):
    return json.loads(str(self.payload_json))

  def __repr__(self): #method defines the format in which the data is displayed returns <Post: (self.body value)>
    return '<UserID: {}, NotifID: {}>\n'.format(self.user_id, self.id)

class Post(SearchableMixin, db.Model): #database model for Posts
  __searchable__ = ['body']
  id = db.Column(db.Integer, primary_key = True)
  body = db.Column(db.String(140), index = True)
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #user.id is a foreign key that connects the Post table with the User table
  language = db.Column('language', db.String(length=5), nullable=True)

  def __repr__(self): #method defines the format in which the data is displayed returns <Post: (self.body value)>
    return '<UserID: {}, PostID: {}, Post: {}, PostTime: {}>\n'.format(self.user_id, self.id, self.body, self.timestamp)

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  body = db.Column(db.String(240))
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

  def __repr__(self):
    return '<Sender ID: {}, Message: {}, Recipient ID: {}>\n'.format(self.sender_id, self.body, self.recipient_id)

