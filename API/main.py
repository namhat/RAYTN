from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name found.")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single&limit=50"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    if result.status_code != 200:
        print(f"Error getting albums: {result.status_code} {result.text}")
        return None

    json_result = json.loads(result.content)["items"]
    albums = [{"name": album["name"], "release_date": album["release_date"], "id": album["id"]} for album in json_result]
    return albums

def get_tracks_in_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    if result.status_code != 200:
        print(f"Error getting tracks: {result.status_code} {result.text}")
        return None

    json_result = json.loads(result.content)["items"]
    tracks = [{"name": track["name"], "duration_ms": track["duration_ms"], "id": track["id"]} for track in json_result]
    return tracks

def get_related_artists(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    if result.status_code != 200:
        print(f"Error getting related artists: {result.status_code} {result.text}")
        return None

    json_result = json.loads(result.content)["artists"]
    related_artists = [{"name": artist["name"], "id": artist["id"], "genres": artist["genres"]} for artist in json_result]
    return related_artists

def search_for_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    if result.status_code != 200:
        print(f"Error searching for track: {result.status_code} {result.text}")
        return None

    json_result = json.loads(result.content)["tracks"]["items"]
    if len(json_result) == 0:
        print("No track with this name found.")
        return None

    return json_result[0]

token = get_token()
result = search_for_artist(token, "bruno")
print(result["name"])
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)

for idx, song in enumerate(songs):
    print(f"{idx+1}. {song['name']}")