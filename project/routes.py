from flask import render_template, flash, redirect, url_for, request
from project import app, db
from project.forms import LoginForm, RegistrationForm, PostForm, RoomLoginForm, CreateRoomForm, FindRoomForm, SongQueryForm, SongSelectForm
from flask_login import current_user, login_user, logout_user, login_required
from project.models import User, Song, Room, List
from werkzeug.urls import url_parse
from datetime import datetime
from project.lookup import lookup
import spotipy
import random
import string

#TODO find a better way to generate roomid

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Select Room')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('index')
        login_user(user, remember=form.remember_me.data)
        return redirect(next_page)
    return render_template('login.html', title="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('New user has been added.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/createroom', methods=['GET', 'POST'])
def createroom():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = CreateRoomForm()
    if form.validate_on_submit():
        roomid = generateRandRoomid()

        while(Room.query.filter_by(roomid=roomid).first() is not None):
            roomid = generateRandRoomid()

        newroom = Room(roomid=roomid, ownerid=current_user.id)
        db.session.add(newroom)
        newroom.add_user(current_user)
        newroom.set_password(form.password.data)
        
        suggest_list = List()
        gen_list = List()
        newroom.set_suggest_list(suggest_list)
        newroom.set_gen_list(gen_list)
        db.session.add(suggest_list)
        db.session.add(gen_list)
        db.session.commit()

        flash('Room ' + roomid + ' successfully created.')
        return redirect(url_for('room', roomid=roomid))
    return render_template('createroom.html', title='Create Room', form=form)
 
def generateRandRoomid():
    return ''.join([random.choice(string.ascii_lowercase) for i in range(5)])

@app.route('/room/<roomid>')
@login_required
def room(roomid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    room = Room.query.filter_by(roomid=roomid).first()
    suggest_list = List.query.filter_by(listid=room.suggest_listid).first().list_songs()
    gen_list = List.query.filter_by(listid=room.gen_listid).first().list_songs()

    if room is None:
        redirect(url_for('createroom'))
    elif not room.check_user(current_user):
         return redirect(url_for('roomlogin', roomid=roomid))
    elif room.check_owner(current_user):
         return render_template('room.html', room=room, suggest_list=suggest_list, gen_list=gen_list) 
    #give owner privileges later
    return render_template('room.html', room=room, suggest_list=suggest_list, gen_list=gen_list)

@app.route('/roomlogin/<roomid>', methods=['GET', 'POST'])
def roomlogin(roomid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RoomLoginForm()
    room = Room.query.filter_by(roomid=roomid).first()
    if room is None:
        flash('Room does not currently exist.')
        return redirect(url_for('roomlogin', roomid=roomid))
    elif room.check_user(current_user):
        return redirect(url_for('room', roomid=roomid))
    elif form.validate_on_submit():
        if not room.check_password(form.password.data):
            flash('Invalid password.')
            return redirect(url_for('roomlogin', roomid=roomid))
        else:
            room.add_user(current_user)
            db.session.commit()
            return redirect(url_for('room', roomid=roomid))
    return render_template('roomlogin.html', title="Login to Room " + roomid, form=form)

@app.route('/findroom', methods=['GET', 'POST'])
def findroom():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = FindRoomForm()
    if form.validate_on_submit():
        room = Room.query.filter_by(roomid=form.roomid.data).first()
        if room is None:
            flash('Room not found.')    
            return redirect(url_for('findroom'))
        else:
            return redirect(url_for('roomlogin', roomid=form.roomid.data))
    return render_template('findroom.html', title='Find Room', form=form)

@app.route('/suggest/<roomid>', methods=['GET', 'POST'])
def findsong(roomid):
    not_authenticated, ret = check_authenticated(roomid)
    if not_authenticated:
        return ret

    form1 = SongQueryForm()
    show = False

    if form1.submit1.data and form1.validate():
        return redirect(url_for('selectsong', roomid=roomid, query=form1.userquery.data))
    
    return render_template('suggest.html', form1=form1, show=show)

@app.route('/suggest/<roomid>/q=<query>', methods=['GET', 'POST'])
def selectsong(roomid, query):
    not_authenticated, ret = check_authenticated(roomid)
    if not_authenticated:
        return ret
    room = ret

    form1 = SongQueryForm()
    form2 = SongSelectForm()
    form2.choices.choices = []

    suggestions = lookup.suggested_list(query, 5)
    form2.choices.choices = []
    album_covers = []

    #TODO right now the site makes a second call to spotipy in order to ensure validation
    #     maybe it would be better to store all suggestions and repopulate list using stored 
    #     suggestions in the database. Otherwise make sure to fix this when adding js
    for i in range(0, len(suggestions)):
        suggestion = suggestions[i]
        form2.choices.choices.append((suggestion.spotify_url, "\"" + suggestion.name + "\" by " + suggestion.main_artist()))
        album_covers.append(suggestion.album_cover)

    if form1.submit1.data and form1.validate():
        return redirect(url_for('selectsong', roomid=roomid, query=form1.userquery.data))
    elif form2.submit2.data and form2.validate():
        #TODO better names
        chosen = lookup.get_track(form2.choices.data)
    
        db_song = Song.query.filter_by(spotify_url=chosen.spotify_url).first()
        if db_song == None:
            db_song = Song(name=chosen.name, artist=chosen.main_artist(), spotify_url=chosen.spotify_url)
            db.session.add(db_song)

        sug_list = List.query.filter_by(listid=room.suggest_listid).first()
        sug_list.add_song(db_song)
        db.session.commit()
        
        flash("Song " + db_song.name + " added.")
        return redirect(url_for('room', roomid=roomid))
 
    return render_template('suggest.html', form1=form1, form2=form2, show=True, album_covers=album_covers)

def check_authenticated(roomid):
    #TODO standardize authentication methods
    if not current_user.is_authenticated:
        return (True, redirect(url_for('login')))
    room = Room.query.filter_by(roomid=roomid).first()
    if room is None:
        return (True, redirect(url_for('createroom')))
    elif not room.check_user(current_user):
        return (True, redirect(url_for('roomlogin', roomid=roomid)))
    return (False, room)
