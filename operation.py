import os
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.client import SpotifyException


CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
LIMIT = 10

class User:
    own = None
    friend = None

user = User()
user.own, operation, user.friend = sys.argv[1:4]


if not CLIENT_ID or not CLIENT_SECRET:
    print("[error] CLIENT_ID or CLIENT_SECRET are not correct")
    print("""
        CLIENT_ID: `{}`
        CLIENT_SECRET: `{}`""".format(CLIENT_ID, CLIENT_SECRET))
    sys.exit(1)

def sorted_print(collection):
    for element in sorted(collection, key=collection.get, reverse=True)[:LIMIT]:
        print(collection[element], "\t", element)

def user_playlists(user, own=True):
    result = []

    try:
        playlists = sp.user_playlists(user)

        for playlist in playlists["items"]:
            if own:
                if playlist["owner"]["id"] == user:
                    result.append(playlist["id"])
            else:
                result.append(playlist["id"])

        return result
    except SpotifyException as e:
        print("ERROR! {}".format(e))


def playlist_songs(user, playlists):
    result = set()

    mapping = {}
    images = {}

    popularity = {}

    for playlist in playlists:
        try:
            songs = sp.user_playlist(user, playlist, fields="tracks,next")
            for song in songs["tracks"]["items"]:
                url = song["track"]["external_urls"].get("spotify", "")
                name = song["track"]["name"]
                group = song["track"]["artists"][0]["name"]

                result.add(url)
                mapping[url] = "{} - {}".format(name, group)
                if group in popularity:
                    popularity[group] += 1
                else:
                    popularity[group] = 1
        except SpotifyException as e:
            pass

    return result, mapping, popularity


if __name__ == '__main__':
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
    )

    play_own = user_playlists(user.own)
    play_friend = user_playlists(user.friend)

    songs_own, mapping_own, popular_own = playlist_songs(user.own, play_own)
    songs_friend, mapping_friend, popular_friend = playlist_songs(user.friend, play_friend)


    # Probably better using a proper parser
    # But it's a 40' hack!

    if operation == '&':
        result = songs_own & songs_friend
    elif operation == '-':
        result = songs_own - songs_friend
    elif operation == '|':
        result = songs_own | songs_friend

    mapping = mapping_own.copy()
    mapping.update(mapping_friend)


    print("\nOperation => `{}`".format(operation))
    print("\nResult of operation:")

    song = None
    for song in result:
        print(mapping[song])
    if song is None:
        print("Operation resulted in empty set :(")


    print("\nMost popular artists for you")
    print("============================")
    sorted_print(popular_own)

    print("\nMost popular artists for {}".format(user.friend))
    print("========================="+"="*len(user.friend))
    sorted_print(popular_friend)
