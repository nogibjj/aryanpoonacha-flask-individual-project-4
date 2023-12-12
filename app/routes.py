from flask import render_template, request, redirect
from app import app

import requests
from urllib.parse import urlencode

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

def parse_url(d):
    x = {k: v for k, v in d.items() if v}
    return urlencode(x)

auth = SpotifyOAuth(cache_path=".spotifycache", scope= 'playlist-read-private')

def getSPOauthURI():
    auth_url = auth.get_authorize_url()
    return auth_url

@app.route('/')
@app.route('/index')
def index():

    #the spotify API stuff
    token_info = auth.get_cached_token()
    
    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = auth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = auth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        playlists = sp.user_playlists('odzw6q69cj4vyz7rcxg8amgwk')
        info = []
        for playlist in playlists['items']:
            info.append(playlist['name'])


    #the beat saver API stuf 
    request = "https://api.beatsaver.com/search/text/0?"
    request_params = {'automapper' : "", 'chroma' : "", 'cinema' : "", 'curated' : "", 'fullSpread' : "", 'maxDuration': "", 'maxRating' : 1.0, 'minRating' : 0, 'q' : "", 'ranked' : "", 'sortOrder' : "Relevance"}
    songcount = 0
    request_params['q'] = 'Taylor Swift'
    final_request = request + parse_url(request_params)
    response = requests.get(request)

    
    return render_template('index.html', title='Beatspotify', data = info)

@app.route("/callback")
def callback():
    url = request.url
    code = auth.parse_response_code(url)
    token = auth.get_access_token(code)
    print("me")
    # Once the get_access_token function is called, a cache will be created making it possible to go through the route "/" without having to login anymore
    return redirect("/")