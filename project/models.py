from project import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime


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

auth_users = db.Table('auth_users', 
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(10), index=True, unique=True)
    suggest_list_id = db.Column(db.String(11))
    gen_list_id = db.Column(db.String(11))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    password_hash = db.Column(db.String(128))
    last_used = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    authorized = db.relationship('User', secondary=auth_users, lazy='dynamic')
    
    def __repr__(self):
        return '<Room {}>'.format(self.room_id)

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

    def set_suggest_list(self, list):
        self.suggest_list_id = self.room_id + '1'
        list.room_id = self.room_id
        list.list_id = self.suggest_list_id
        db.session.commit()

    def set_gen_list(self, list):
        self.gen_list_id = self.room_id + '2'
        list.room_id = self.room_id
        list.list_id = self.gen_list_id
        db.session.commit()

song_lists = db.Table('song_lists',
    db.Column('list_id', db.Integer, db.ForeignKey('list.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    spotify_url = db.Column(db.String(200))

    def __repr__(self):
        return '<Song {}>'.format(self.name)

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.String(11))
    room = db.Column(db.Integer, db.ForeignKey('room.id'))
    songs = db.relationship('Song', secondary=song_lists, lazy='dynamic')    

    def add_song(self, song):
        if not self.check_song(song):
            self.songs.append(song)

    def check_song(self, song):
        return self.songs.filter(
            song_lists.c.song_id == song.id).count() > 0

    def list_songs(self):
        #TODO naming
        ret = []
        for song in self.songs:
           ret.append([song.name, song.artist, song.spotify_url])
        return ret 
    
    def __repr__(self):
        return '<List>' #TODO

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
