import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

print("--- Testing Alternatives ---")

# Use a known artist ID (The Beatles)
artist_id = '3WrFJ7ztbogyGnTHbHJFl2' 

# Test 1: Related Artists
print("\n1. Testing Related Artists...")
try:
    related = sp.artist_related_artists(artist_id)
    print(f"   ✅ Success! Found {len(related['artists'])} related artists.")
    print(f"   Example: {related['artists'][0]['name']}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 2: Artist Top Tracks
print("\n2. Testing Artist Top Tracks...")
try:
    top = sp.artist_top_tracks(artist_id)
    print(f"   ✅ Success! Found {len(top['tracks'])} top tracks.")
    print(f"   Example: {top['tracks'][0]['name']}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
