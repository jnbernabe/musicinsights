import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# Load .env
load_dotenv()

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

print("--- Spotify Deep Verification 2.0 ---")

try:
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    token = auth_manager.get_access_token(as_dict=False)
    
    # Test 1: Seed Genres (Simpler)
    print("\n1. Testing recommendations with seed_genres=['pop']...")
    try:
        res = sp.recommendations(seed_genres=['pop'], limit=1)
        print("   ✅ Genres worked!")
    except Exception as e:
        print(f"   ❌ Genres failed: {e}")

    # Test 2: Raw Request (Bypass Spotipy)
    print("\n2. Testing Raw HTTP Request for Tracks...")
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/recommendations?limit=1&seed_tracks=44MuEHdlociG8KjhPhOVw5"
    
    response = requests.get(url, headers=headers)
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")

except Exception as e:
    print(f"Error: {e}")
