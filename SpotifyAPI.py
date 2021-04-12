import datetime
import time
import webbrowser
from urllib.parse import urlencode
from furl import furl
from pywinauto import Application

from init import getProperties
import requests
import base64


class SpotifyAPI(object):
    accessToken = None
    accessTokenExpires = datetime.datetime.now()
    clientId = None
    tokenUrl = "https://accounts.spotify.com/api/token"
    isAccessTokenExpired = True

    def __init__(self, clientId, clientSecret):
        super().__init__()
        self.clientId = clientId
        self.clientSecret = clientSecret

    def getAuthCode(self):
        # Initialize request parameters
        endpoint = "https://accounts.spotify.com/authorize"
        data = urlencode({
            "client_id": self.clientId,
            "scope": "user-modify-playback-state user-read-currently-playing",
            "response_type": "code",
            "redirect_uri": "http://localhost:4996/callback"
        })
        # Create look up URL with encoding
        lookupUrl = f"{endpoint}?{data}"

        # Open newest browser tab and extract URL
        webbrowser.open(lookupUrl)
        time.sleep(3)
        app = Application(backend='uia')
        app.connect(title_re=".*Chrome.*")
        element_name = "Address and search bar"
        dlg = app.top_window()
        redirectedUrl = dlg.child_window(title=element_name, control_type="Edit").get_value()

        # Format URL to get 'code' value from parameters
        fUrl = furl(redirectedUrl)
        authCode = fUrl.args['code']
        return authCode

    def getClientCredentials(self):
        """
        :return: encoded base64 credentials string
        """
        clientCredentials = f"{self.clientId}:{self.clientSecret}"
        clientCredentialsBase64 = base64.b64encode(clientCredentials.encode())
        return clientCredentialsBase64.decode()

    def getTokenHeaders(self):
        clientCredentialsBase64 = self.getClientCredentials()
        return {
            "Authorization": f"Basic {clientCredentialsBase64}"
        }

    def authenticate(self):
        # Initialize variables for Authorization
        code = self.getAuthCode()
        endpoint = self.tokenUrl
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:4996/callback"
        }
        tokenHeaders = self.getTokenHeaders()

        r = requests.post(endpoint, data=data, headers=tokenHeaders)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate!")

        responseData = r.json()

        now = datetime.datetime.now()
        # Get access_token from response, calculate its expiration time
        accessToken = responseData['access_token']
        self.accessToken = accessToken
        expiresIn = responseData['expires_in']  # seconds
        expires = now + datetime.timedelta(seconds=expiresIn)
        self.accessTokenExpires = expires
        self.isAccessTokenExpired = expires < now
        return True

    def getToken(self):
        """
        :return: Token for authorization
        """
        token = self.accessToken
        expires = self.accessTokenExpires
        now = datetime.datetime.now()
        # Get new token if old expired
        if expires < now:
            self.authenticate()
            return self.getToken()
        return token

    def nextSong(self):
        accessToken = self.getToken()
        endpoint = "https://api.spotify.com/v1/me/player/next"
        headers = {
            "Authorization": f"Bearer {accessToken}"
        }
        r = requests.post(endpoint, headers=headers)
        if r.status_code in range(200, 299):
            return print("Switched to next song!")

    def getCurrentSong(self):
        accessToken = self.getToken()
        endpoint = "https://api.spotify.com/v1/me/player/currently-playing"
        data = urlencode({
            "market": "LT",
            "additional_types": "track"
        })
        lookUpUrl = f"{endpoint}?{data}"
        headers = {
            "Authorization": f"Bearer {accessToken}"
        }
        r = requests.get(endpoint, headers=headers)
        if r.status_code in range(200, 299):
            receivedData = r.json()
            artist = receivedData['item']['artists'][0]['name']
            song = receivedData['item']['name']
            artistSong = artist + ' - ' + song
            return artistSong, print(artistSong)


clientId, clientSecret = getProperties()
spotify = SpotifyAPI(clientId, clientSecret)
spotify.getToken()


while True:
    command = input("Enter Command:\n")
    if command == "!next":
        spotify.nextSong()
    elif command == "!song":
        spotify.getCurrentSong()
    elif command == "!quit":
        break
    else:
        print("Incorrect command!")

