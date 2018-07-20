import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def create_playlist(name):
    client_credentials_manager = SpotifyClientCredentials(client_id=cred.client_id, client_secret=cred.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.user_playlist_create(cred.client_username, name)

def add_to_playlist(playlist_id, song):
    client_credentials_manager = SpotifyClientCredentials(client_id=cred.client_id, client_secret=cred.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.user_playlist_add_tracks(cred.client_username, playlist_id, songs)
