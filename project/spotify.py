import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from project.lookup import cred
from flask import redirect

def create_playlist(name):
    sp = spotipy.Spotify(auth='BQDpwmu5IqF4KopCSn11J-DdvSXJxz2-rWptMuurQ_lWk2p5n6ES6izN_0G7IRz_sJI-3uafxO-h-CI20WqRwEYkeid85zQAniy_w1bBRsdwPp9L7L1jekddP6ToE6TZ9xUyZheFZnXZyzV8HZjGS-lX0v_VnyQjc3dYzskizS5CqwQIiCJsfZnC4yEXam-0eWN9IjkmBZcIwJUT9mTVlmIDqxmiDD3l33UuciHNZqDg')
    return sp.user_playlist_create(cred.client_username, name)

def add_to_playlist(playlist_id, songs):
    sp = spotipy.Spotify(auth='BQDpwmu5IqF4KopCSn11J-DdvSXJxz2-rWptMuurQ_lWk2p5n6ES6izN_0G7IRz_sJI-3uafxO-h-CI20WqRwEYkeid85zQAniy_w1bBRsdwPp9L7L1jekddP6ToE6TZ9xUyZheFZnXZyzV8HZjGS-lX0v_VnyQjc3dYzskizS5CqwQIiCJsfZnC4yEXam-0eWN9IjkmBZcIwJUT9mTVlmIDqxmiDD3l33UuciHNZqDg')
    sp.user_playlist_add_tracks(cred.client_username, playlist_id, songs)

def reset_and_add_to_playlist(playlist_id, songs):
    sp = spotipy.Spotify(auth='BQDpwmu5IqF4KopCSn11J-DdvSXJxz2-rWptMuurQ_lWk2p5n6ES6izN_0G7IRz_sJI-3uafxO-h-CI20WqRwEYkeid85zQAniy_w1bBRsdwPp9L7L1jekddP6ToE6TZ9xUyZheFZnXZyzV8HZjGS-lX0v_VnyQjc3dYzskizS5CqwQIiCJsfZnC4yEXam-0eWN9IjkmBZcIwJUT9mTVlmIDqxmiDD3l33UuciHNZqDg')
    sp.user_playlist_replace_tracks(cred.client_username, playlist_id, songs)

def login_to_user_spotify():
    
    #Need to more access to user data? Add more scopes here!
    SCOPE = 'playlist-read-private user-library-read playlist-modify-public playlist-modify-private'
    CACHE = '.spotipyoauthcache'
    SPOTIPY_REDIRECT_URI = redirect(url_for('index'))
    #TODO determine where to redirect after authorization by putting URI in SPOTIPY_REDIRECT_URI
    sp_oauth = oauth2.SpotifyOAuth(cred.client_id, cred.client_secret,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE)
    
    print(sp_oauth.get_cached_token())
    print(sp_oauth.is_token_expired())