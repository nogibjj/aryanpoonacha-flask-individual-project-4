from os import environ

FLASK_ENV = environ.get('FLASK_ENV')
FLASK_DEBUG = environ.get('FLASK_DEBUG')
FLASK_APP = environ.get('FLASK_APP')
SECRET_KEY = environ.get('environ.get')
FLASK_RUN_HOST=environ.get('FLASK_RUN_HOST')
FLASK_RUN_PORT=environ.get('FLASK_RUN_PORT')

SPOTIPY_CLIENT_ID=environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET=environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = environ.get('SPOTIPY_REDIRECT_URI')