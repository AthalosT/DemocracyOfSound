from project import socketio
from flask_socketio import send, emit
from project.lookup import lookup

@socketio.on('song-query')
def handle_song_query(query):
    suggestions = lookup.suggested_list(query, 5)
    emit('song-query-results', [vars(suggestion) for suggestion in suggestions])
