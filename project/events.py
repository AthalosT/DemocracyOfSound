from project import socketio
from flask_socketio import send, emit
from project import db
from project.lookup import lookup
from project.models import Room, List, Song


@socketio.on('joined')
def updated_playlist(data):
    room_id = str(data['room_id'])
    room = Room.query.filter_by(room_id=room_id).first()
    if room is not None:
        sug_list = List.query.filter_by(list_id=room.suggest_list_id).first()
        sug_list_songs = sug_list.list_songs()
        if len(sug_list_songs) > 0:
            emit('updated-sug-list', [song for song in sug_list_songs])

@socketio.on('song-query')
def handle_song_query(query):
    suggestions = lookup.suggested_list(query, 5)
    emit('song-query-results', [vars(suggestion) for suggestion in suggestions])

@socketio.on('song-selection')
def handle_song_selection(selection_data):
    spotify_url = selection_data['spotify_url']
    room_id = selection_data['room_id']
    room = Room.query.filter_by(room_id=room_id).first()
    if room is not None:
        chosen = lookup.get_track(spotify_url)
        db_song = Song.query.filter_by(spotify_url=spotify_url).first()
        if db_song is None:
            db_song = Song(name=chosen.name, artist=chosen.main_artist(), spotify_url=chosen.spotify_url)
            db.session.add(db_song)

        sug_list = List.query.filter_by(list_id=room.suggest_list_id).first()
        sug_list.add_song(db_song)
        db.session.commit()
        sug_list_songs = sug_list.list_songs()
        emit('updated-sug-list', [song for song in sug_list_songs], broadcast=True)
    else:
        emit('failed', "Sorry, the song was not added. Please try again.")
