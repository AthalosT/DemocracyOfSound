from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from project.lookup import selection, cred


def suggested_list(input_str, num_args):
    
    client_credentials_manager = SpotifyClientCredentials(client_id=cred.client_id,
                                                          client_secret=cred.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.search(q=input_str, limit=num_args)

    suggestions = []

    for i, t in enumerate(results['tracks']['items']):
        
        artists = []
        for j in t['artists']:
            artists.append(j['name'])

        temp = selection.Selection(name=t['name'], artists=artists, explicit=t['explicit'],
                                   spotify_url=t['external_urls']['spotify'], 
                                   preview_url=t['preview_url'], album_cover=t['album']['images'][0]['url'])
        suggestions.append(temp)

    return suggestions
