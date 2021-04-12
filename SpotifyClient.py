import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyClient(object):

    scope = "user-library-read"

    def authorize(self):
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        return "Authorized Successfully!"

client = SpotifyClient()
client.authorize()