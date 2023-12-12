"""
Prerequisites
    pip3 install spotipy Flask Flask-Session
    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py
 
    // on Windows, use `SET` instead of `export`
Run app.py
    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

import os, shutil
from tkinter import E
from flask import Flask, session, request, redirect, render_template, send_file
from flask_session import Session
import spotipy
import uuid

import requests
from urllib.parse import urlencode

import string
import random
from zipfile import ZipFile
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('index.html', auth_url = auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template('main.html', name = spotify.me()["display_name"])
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
		   f'<a href="/current_user">me</a>' \


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlists = spotify.current_user_playlists()
    playlist_urls = []
    playlist_ids = []
    for playlist in playlists['items']:
        playlist_urls.append("https://open.spotify.com/embed/playlist/" + playlist['id'])
        playlist_ids.append(playlist['id'])
    return render_template("playlists.html", playlists = zip(playlist_ids, playlist_urls))

@app.route('/playlist/<id>', methods=['GET', 'POST'])
def playlist(id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    if request.method == 'GET':
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        playlist_id = id
        print(spotify.me()['id'])
        results = spotify.user_playlist_tracks(spotify.me()['id'],playlist_id)
        tracks = results['items']
        while results['next']:
            results = spotify.next(results)
            tracks.extend(results['items'])
    
        names_list= []
        song_numbers = []
        count = 0
        #name = results['items'][0]['track']['name']
        for song in tracks:
            names_list.append(song['track']['name'])
            song_numbers.append("song"+str(count))
            count+=1

        return render_template('playlist.html', songs = zip(names_list, song_numbers))

    return 'ligma'


def parse_url(d):
    x = {k: v for k, v in d.items() if v}
    return urlencode(x)

def zip_directory(folder_path, zip_path):
    with ZipFile(zip_path, mode='w') as zipf:
        len_dir_path = len(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])

@app.route('/conversion', methods=['POST'])
def conversion():
    json_data = request.json
    print(json_data)
    songcount = 0
    request_params = {'automapper' : "", 'chroma' : "", 'cinema' : "", 'curated' : "", 'fullSpread' : "", 'maxDuration': "", 'maxRating' : 1.0,
    'minRating' : 0, 'q' : "", 'ranked' : "", 'sortOrder' : "Relevance", 'maxBpm' : '', 'minBpm' : ''}
    
    if(json_data.get('automapper')):
            request_params['automapper'] = 'true'
    if(json_data.get('chroma')):
            request_params['chroma'] = 'true'
    if(json_data.get('cinema')):
            request_params['cinema'] = 'true'
    if(json_data.get('curated')):
            request_params['curated'] = 'true'
    if(json_data.get('fullSpread')):
            request_params['fullSpread'] = 'true'
    if(json_data['maxDuration'] != ''):
            request_params['maxDuration'] = json_data['maxDuration']
    if(json_data['minDuration'] != ''):
            request_params['minDuration'] = json_data['minDuration']
    if(json_data['minRating'] != ''):
            request_params['minRating'] = json_data['minRating']
    if(json_data['maxRating'] != ''):
            request_params['maxRating'] = json_data['maxRating']
    if(json_data['maxBpm'] != ''):
            request_params['maxBpm'] = json_data['maxBpm']
    if(json_data['minBpm'] != ''):
            request_params['minBpm'] = json_data['minBpm']
    
    #generate a temp folder name
    letters = string.ascii_letters
    temp_folder = ''.join(random.choice(letters) for i in range(10))
    os.mkdir("temp/"+temp_folder)
    banned_chars =['/', '\\', '*','?', ':', "\"", '<', '>', '|']

    while(json_data.get('song'+str(songcount))):

        request_params['q'] = json_data['song'+str(songcount)]
        request_url = "https://api.beatsaver.com/search/text/0?"

        #API request to search for song
        final_request = request_url + parse_url(request_params)
        response = requests.get(final_request)
        

        #extract the download URL for the best match of this song
        if(response.json()['docs']):
            download_url = response.json()['docs'][0]['versions'][0]['downloadURL']
        else:
            songcount+=1
            continue

        #download the song and store it in a temp folder
        downloaded_obj = requests.get(download_url, stream=True)
        filename = json_data['song'+str(songcount)] + ".zip"
        for c in banned_chars:
            if c in filename:
                filename = filename.replace(c, '')

        
        #download the file
        with open("temp/" + temp_folder + "/"+ filename,"wb+") as file:
            file.write(downloaded_obj.content)

        #unzip the file
        with ZipFile("temp/" + temp_folder + "/"+ filename, 'r') as zipObj:
            zipObj.extractall("temp/" + temp_folder + "/" +filename[:-4])

        #delete the zip file
        os.remove("temp/" + temp_folder + "/"+ filename)
        songcount+=1
        

    #zip the whole folder
    zip_directory('temp/' + temp_folder, "temp/" + temp_folder + ".zip")

    #delete the temp folder 
    dir = 'temp/' + temp_folder
    for files in os.listdir(dir):
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)
    os.rmdir('temp/' + temp_folder)

    return send_file('temp/' + temp_folder+".zip", as_attachment=True)


@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()

'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=8080)


    