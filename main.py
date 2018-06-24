from project import app, db
from project.models import User, Song, Room, List

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Song': Song, 'Room': Room, 'List': List}
