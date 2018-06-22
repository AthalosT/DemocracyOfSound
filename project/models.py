from project import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from sqlalchemy import PickleType


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    artist = db.Column(db.String(40))
    spotify_url = db.Column(db.String(200))

    def __repr__(self):
        return '<Song {}>'.format(self.name)

auth_users = db.Table('auth_users', 
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomid = db.Column(db.String(10), index=True, unique=True)
    listid = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    password_hash = db.Column(db.String(128))
    lastused = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    authorized = db.relationship("User", secondary=auth_users, lazy='dynamic')
    
    def __repr__(self):
        return '<Room {}>'.format(self.roomid)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_user(self, user):
        if not self.check_user(user):
            self.authorized.append(user)
    
    def check_user(self, user):
        return self.authorized.filter(
            auth_users.c.user_id == user.id).count() > 0

    def check_owner(self, user):
        return self.owner_id == user.id

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.Integer, db.ForeignKey('room.id'))
    song_list = db.Column(PickleType)

    def __repr__(self):
        return '<List>'
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
