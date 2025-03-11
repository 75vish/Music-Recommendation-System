import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "59b536bc16314a3584f982a131a31a42"
CLIENT_SECRET = "79f1dbbc62a446daa92f2d2ebc6e7faf"

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music["song"] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)
    return recommended_music_names, recommended_music_posters

# Initialize session states
if 'playlists' not in st.session_state:
    st.session_state.playlists = {}
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

music = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))
music_list = music["song"].values

# Sidebar main menu selection with larger title
st.sidebar.markdown("<h2 style='text-align: center;'>Main Menu</h2>", unsafe_allow_html=True)
section = st.sidebar.radio("", ["Recommendations", "Playlists"])

if section == "Recommendations":
    st.header("Music Recommender System")
    selected_song = st.selectbox("Type or select a song from the dropdown", music_list)
    if st.button("Show Recommendation"):
        st.session_state.recommendations = recommend(selected_song)

    # Display recommendations if they exist in the session state
    if st.session_state.recommendations:
        recommended_music_names, recommended_music_posters = st.session_state.recommendations
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(recommended_music_names[idx])
                st.image(recommended_music_posters[idx])

                # Add to playlist options
                playlist_name = st.text_input(f"Playlist Name for {recommended_music_names[idx]}", key=f"playlist_input_{idx}")
                if st.button("Add to Playlist", key=f"add_{recommended_music_names[idx]}"):
                    if playlist_name:
                        # Initialize playlist if it doesn't exist
                        if playlist_name not in st.session_state.playlists:
                            st.session_state.playlists[playlist_name] = []
                        # Add song to specified playlist
                        st.session_state.playlists[playlist_name].append({
                            'name': recommended_music_names[idx],
                            'cover': recommended_music_posters[idx]
                        })
                        st.success(f'Added "{recommended_music_names[idx]}" to playlist "{playlist_name}"')
                    else:
                        st.error("Please enter a playlist name.")

elif section == "Playlists":
    st.header("Your Playlists")
    for playlist_name, songs in st.session_state.playlists.items():
        with st.expander(playlist_name, expanded=False):
            if songs:
                for song in songs:
                    # Display each song in a row format
                    song_col = st.columns([1, 3])
                    with song_col[0]:
                        st.image(song['cover'], width=100)
                    with song_col[1]:
                        st.write(song['name'])
            else:
                st.write("This playlist is empty.")
    
    # Option to clear a specific playlist
    clear_playlist_name = st.text_input("Playlist Name to Clear", key="clear_playlist_input")
    if st.button("Clear Playlist"):
        if clear_playlist_name in st.session_state.playlists:
            del st.session_state.playlists[clear_playlist_name]
            st.success(f'Playlist "{clear_playlist_name}" cleared.')
        else:
            st.error("Playlist not found.")
