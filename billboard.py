import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pprint import pprint

user_in = input("What year would you like to travel to? Type the date in this format: YYYY-MM-DD ")

res = requests.get(f"https://www.billboard.com/charts/hot-100/{user_in}/")
res.raise_for_status()
web_res = res.text
soup = BeautifulSoup(web_res, "html.parser")

bill_song = soup.select("li ul li h3")
bill_artist = soup.select("li ul li span")
song_list = []
for i in bill_song:
    song_list.append((i.getText()).strip())
artist = [(art.getText()).strip() for art in bill_artist]
# print(song_list)
# print(artist)
artist_list = []
for n in artist:
    if not n.isdigit() and n != "-":
        artist_list.append(n)

# print(artist_list)
# print(len(artist_list))
year_in = int(user_in.split("-")[0])
song_and_artist = dict(zip(song_list, artist_list))

print(song_and_artist)


def spotify_autho():
    #Credentias should be stored in Env, for authentication to work
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private",
                                                   show_dialog=True,
                                                   cache_path="token.txt"))

    user_id = sp.current_user()['id']
    return sp


def get_song_uri(song_and_artist: dict, year_release):
    uri_list = []
    sp = spotify_autho()
    skippped_list = []
    for (song, arti) in song_and_artist.items():
        res = sp.search(q=f"track:{song} year:{year_release}", type="track", limit=1, offset=1)
        try:
            uri = res['tracks']['items'][0]['uri']
            uri_list.append(uri)
        except IndexError:
            skippped_list.append(song)
            print(f"{song} by {arti} doesn't exist in spotify. Skipped, trying again..")
            try:
                re_search = sp.search(q=f"track:{song}", type="track", limit=1, offset=1)
                re_uri = re_search['tracks']['items'][0]['uri']
                uri_list.append(re_uri)
            except:
                pass
    print(f"Total number of he songs found: {len(uri_list)}")
    #print(uri_list)
    return uri_list


def create_playlist():
    sp = spotify_autho()
    local_user = sp.current_user()['id']
    print(f"Current User ID: {local_user} ")
    new_play = sp.user_playlist_create(user=local_user, name=f"{user_in} Billboard top 100", public=False)
    return new_play


def add_songs_to_playlist(song_list: list, created_playlist_id):
    sp = spotify_autho()
    sp.playlist_add_items(playlist_id=created_playlist_id, items=song_list)
    print(f"New Playlist {user_in} Billboard top 100 successfully created on Spotify!")


top_100 = get_song_uri(song_and_artist, year_release=year_in)
new_playlist = create_playlist()
current_playlist_id = new_playlist['id']

add_songs_to_playlist(top_100,current_playlist_id)