from project import db,login_manager
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

participated_events = db.Table('participated_events',
        db.Column('participent_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
        )

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(50),unique=True,nullable=False)
    image_file = db.Column(db.String(120),nullable=False,default='default.jpg')
    password_hash = db.Column(db.String(160),nullable=False)
    email_varified = db.Column(db.Boolean, nullable=False, default=False)
    events = db.relationship('Event',backref='author',lazy=True)
    participated_events = db.relationship(
            'Event',secondary=participated_events, backref='participents', lazy=True)


    def __init__(self,*,username,email,password,image_file=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        if image_file:
            self.image_file = image_file

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'User(username={self.username},email={self.email}'

class Event(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    title = db.Column(db.String(50),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    event_date = db.Column(db.DateTime,nullable=False)
    state = db.Column(db.String(20),nullable=False)
    city = db.Column(db.String(20),nullable=False)
    place = db.Column(db.String(50),nullable=False)
    category = db.Column(db.String(50),nullable=False) 
    seat = db.Column(db.Integer)
    description = db.Column(db.Text,nullable=False)

    def __repr__(self):
        return f'Event(title{self.title},date_posted={self.date_posted}'

