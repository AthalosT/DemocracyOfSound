from project import socketio
from flask_socketio import send, emit, join_room, leave_room
from project import db
from project.lookup import lookup
from project.models import User, Room, List, Song
import threading


room_id = ""
username = ""

@socketio.on('join')
def updated_playlist(data):
    global room_id
    global username

    room_id = str(data['room_id'])
    username = str(data['username'])
    room = Room.query.filter_by(room_id=room_id).first()
    if room is not None:
        join_room(room_id)
        room.add_current_user(User.query.filter_by(username=username).first())
        db.session.commit()
        emit('update-room-users', room.list_current_users(), room=room_id)

        sug_list = List.query.filter_by(list_id=room.suggest_list_id).first()
        sug_list_songs = sug_list.list_songs()
        if len(sug_list_songs) > 0:
            emit('update-sug-list', [song for song in sug_list_songs])

@socketio.on('disconnect')
def on_disconnect():
    room = Room.query.filter_by(room_id=room_id).first()

    if room is not None:
        user = User.query.filter_by(username=username).first()
        room.remove_current_user(user)
        db.session.commit()
        emit('update-room-users', room.list_current_users(), room=room_id)
        leave_room(room_id)

@socketio.on('song-query')
def handle_song_query(data):
    query = str(data['query'])
    num_selections = int(data['num_selections'])
    suggestions = lookup.suggested_list(query, num_selections)
    emit('song-query-results', [vars(suggestion) for suggestion in suggestions])

@socketio.on('song-selection')
def handle_song_selection(selection_data):
    spotify_url = selection_data['spotify_url']
    #room_id = selection_data['room_id']
    room = Room.query.filter_by(room_id=room_id).first()
    if room is not None:
        chosen = lookup.get_track(spotify_url)
        db_song = Song.query.filter_by(spotify_url=spotify_url).first()
        if db_song is None:
            db_song = Song(name=chosen.name, artist=chosen.main_artist(), spotify_url=chosen.spotify_url)
            db.session.add(db_song)

        sug_list = List.query.filter_by(list_id=room.suggest_list_id).first()
        if not sug_list.add_song(db_song):
            emit('failed', "The song has already been added to the playlist.")
        else:
            db.session.commit()
            sug_list_songs = sug_list.list_songs()
            emit('update-sug-list', [song for song in sug_list_songs], room=room_id)
    else:
        emit('failed', "Sorry, the song was not added. Please try again.")
