from flask import render_template, flash, redirect, url_for, request
from project import app, db
from project.forms import LoginForm, RegistrationForm, PostForm, RoomLoginForm, CreateRoomForm, FindRoomForm, SongQueryForm, SongSelectForm
from flask_login import current_user, login_user, logout_user, login_required
from project.models import User, Selection, Room, List
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
        newroom = Room(roomid=roomid, owner_id=current_user.id)
        db.session.add(newroom)
        newroom.add_user(current_user)
        newroom.set_password(form.password.data)
        db.session.commit()
        flash('Room ' + roomid + ' successfully created.')
        return redirect(url_for('room', roomid=roomid))
    return render_template('createroom.html', title='Create Room', form=form)
 
def generateRandRoomid():
    roomid = ''
    for i in range(0, 5):
        roomid = roomid + random.choice(string.ascii_lowercase)
    return roomid

@app.route('/room/<roomid>')
@login_required
def room(roomid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    room = Room.query.filter_by(roomid=roomid).first()
    if room is None:
        redirect(url_for('createroom'))
    elif not room.check_user(current_user):
         return redirect(url_for('roomlogin', roomid=roomid))
    elif room.check_owner(current_user):
         return render_template('room.html', room=room) #give owner privileges later
    return render_template('room.html', room=room)

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

@app.route('/suggestsong/<roomid>', methods=['GET', 'POST'])
def suggestsong(roomid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    room = Room.query.filter_by(roomid=roomid).first()
    if room is None:
        #redirect somehwere?
        return redirect(url_for('createroom'))
    elif not room.check_user(current_user):
        return redirect(url_for('roomlogin', roomid=roomid))

    form1 = SongQueryForm()
    form2 = SongSelectForm()
    choices = []
    if form1.submit1.data and form1.validate():
        input = form1.userquery.data
        suggestions = lookup.suggested_list(input, 5)
        for s in suggestions:
            choices.append("\"" + s.name + "\"" + " by " + s.main_artist())
        #choices = [input + '1', input + '2', input + '3'] #TODO spotipy method to get choices here
        #return(url_for('suggestsong'))
    elif form2.submit2.data and form2.validate():
        #TODO add song selected to playlist
        flash("Option " + form2.songs.data + " was chosen.")
        #return redirect(url_for('room', roomid=roomid))
    return render_template('suggestsong.html', title='Suggest a Song', form1=form1, form2=form2, choices=choices)

