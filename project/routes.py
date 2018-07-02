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

#TODO find a better way to generate room_id

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
def create_room():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = CreateRoomForm()
    if form.validate_on_submit():
        room_id = generateRandRoomid()

        while(Room.query.filter_by(room_id=room_id).first() is not None):
            room_id = generateRandRoomid()

        new_room = Room(room_id=room_id, owner_id=current_user.id, room_name=form.room_name.data)
        db.session.add(new_room)
        new_room.add_user(current_user)
        new_room.set_password(form.password.data)
        
        suggest_list = List()
        gen_list = List()
        new_room.set_suggest_list(suggest_list)
        new_room.set_gen_list(gen_list)
        db.session.add(suggest_list)
        db.session.add(gen_list)
        db.session.commit()

        flash('Room ' + room_id + ' successfully created.')
        return redirect(url_for('room', room_id=room_id))
    else:
        form.room_name.data = current_user.username + "'s Room"
    return render_template('create-room.html', title='Create Room', form=form)
 
def generateRandRoomid():
    return ''.join([random.choice(string.ascii_lowercase) for i in range(5)])

@app.route('/room/<room_id>')
@login_required
def room(room_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    room = Room.query.filter_by(room_id=room_id).first()
    
    if room is None:
        return redirect(url_for('create_room'))
    elif not room.check_user(current_user):
         return redirect(url_for('room_login', room_id=room_id))

    suggest_list = List.query.filter_by(list_id=room.suggest_list_id).first().list_songs()
    gen_list = List.query.filter_by(list_id=room.gen_list_id).first().list_songs()

    return render_template('room.html', room=room, suggest_list=suggest_list, gen_list=gen_list, username=current_user.username, is_owner=room.check_owner(current_user)) 

@app.route('/roomlogin/<room_id>', methods=['GET', 'POST'])
def room_login(room_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RoomLoginForm()
    current_room = Room.query.filter_by(room_id=room_id).first()
    if room is None:
        flash('Room does not currently exist.')
        return redirect(url_for('room_login', room_id=room_id))
    elif current_room.check_user(current_user):
        return redirect(url_for('room', room_id=room_id))
    elif form.validate_on_submit():
        if not current_room.check_password(form.password.data):
            flash('Invalid password.')
            return redirect(url_for('room_login', room_id=room_id))
        else:
            current_room.add_user(current_user)
            db.session.commit()
            return redirect(url_for('room', room_id=room_id))
    return render_template('room-login.html', title="Login to Room " + room_id, form=form, room_id = room_id)

@app.route('/findroom', methods=['GET', 'POST'])
def find_room():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = FindRoomForm()
    if form.validate_on_submit():
        current_room = Room.query.filter_by(room_id=form.room_id.data).first()
        if current_room is None:
            flash('Room not found.')    
            return redirect(url_for('find_room'))
        else:
            return redirect(url_for('room_login', room_id=form.room_id.data))
    return render_template('find-room.html', title='Find Room', form=form)

@app.route('/suggest/<room_id>', methods=['GET', 'POST'])
def find_song(room_id):
    not_authenticated, ret = check_authenticated(room_id)
    if not_authenticated:
        return ret

    find_song_form = SongQueryForm()
    show = False

    if find_song_form.submit1.data and find_song_form.validate():
        return redirect(url_for('select_song', room_id=room_id, query=find_song_form.user_query.data))
    
    return render_template('suggest.html', find_song_form=find_song_form, show=show)

@app.route('/suggest/<room_id>/q=<query>', methods=['GET', 'POST'])
def select_song(room_id, query):
    not_authenticated, ret = check_authenticated(room_id)
    if not_authenticated:
        return ret
    room = ret

    find_song_form = SongQueryForm()
    select_song_form = SongSelectForm()
    select_song_form.choices.choices = []

    suggestions = lookup.suggested_list(query, 5)
    select_song_form.choices.choices = []
    album_covers = []

    #TODO right now the site makes a second call to spotipy in order to ensure validation
    #     maybe it would be better to store all suggestions and repopulate list using stored 
    #     suggestions in the database. Otherwise make sure to fix this when adding js
    for i in range(0, len(suggestions)):
        suggestion = suggestions[i]
        select_song_form.choices.choices.append((suggestion.spotify_url, "\"" + suggestion.name + "\" by " + suggestion.main_artist()))
        album_covers.append(suggestion.album_cover)

    if find_song_form.submit1.data and find_song_form.validate():
        return redirect(url_for('select_song', room_id=room_id, query=find_song_form.user_query.data))
    elif select_song_form.submit2.data and select_song_form.validate():
        #TODO better names
        chosen = lookup.get_track(select_song_form.choices.data)
    
        db_song = Song.query.filter_by(spotify_url=chosen.spotify_url).first()
        if db_song is None:
            db_song = Song(name=chosen.name, artist=chosen.main_artist(), spotify_url=chosen.spotify_url)
            db.session.add(db_song)

        sug_list = List.query.filter_by(list_id=room.suggest_list_id).first()
        sug_list.add_song(db_song)
        db.session.commit()
        
        flash("Song " + db_song.name + " added.")
        return redirect(url_for('room', room_id=room_id))
 
    return render_template('suggest.html', find_song_form=find_song_form, select_song_form=select_song_form, show=True, album_covers=album_covers)

def check_authenticated(room_id):
    #TODO standardize authentication methods
    if not current_user.is_authenticated:
        return (True, redirect(url_for('login')))
    room = Room.query.filter_by(room_id=room_id).first()
    if room is None:
        return (True, redirect(url_for('create_room')))
    elif not room.check_user(current_user):
        return (True, redirect(url_for('room_login', room_id=room_id)))
    return (False, room)
