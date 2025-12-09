import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

class SpotifyService:
    def __init__(self, client_id, client_secret):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))

    def get_missing_top_tracks(self, playlist_data, limit=10):
        """
        Identify top artists from the playlist, fetch their top tracks from Spotify,
        and return the ones that are NOT already in the playlist ('Deep Cuts').
        """
        try:
            from collections import Counter
            
            # 1. Identify Top Artists & Known Tracks
            artist_counter = Counter()
            known_uris = set()
            
            for entry in playlist_data:
                track = entry.get('track', {})
                # Add to known URIs
                if track.get('uri'):
                    known_uris.add(track['uri'])
                
                # Count artists
                for artist in track.get('artists', []):
                    artist_counter[artist] += 1

            # Get top 5 artists
            top_artists = [name for name, _ in artist_counter.most_common(5)]
            
            recommendations = []
            
            # 2. For each top artist, find missing hits
            for artist_name in top_artists:
                # Search for artist to get ID
                # We limit search to type='artist' and exact match if possible, but search is fuzzy.
                search_res = self.sp.search(q=f"artist:{artist_name}", type='artist', limit=1)
                items = search_res['artists']['items']
                
                if not items:
                    continue
                    
                artist_id = items[0]['id']
                
                # Get their top tracks (returns up to 10)
                top_tracks = self.sp.artist_top_tracks(artist_id)
                
                for track in top_tracks['tracks']:
                    # Check if we already have this song
                    if track['uri'] not in known_uris:
                        # Avoid duplicates in recommendations list itself
                        if not any(r['id'] == track['id'] for r in recommendations):
                            recommendations.append({
                                'name': track['name'],
                                'artists': [artist['name'] for artist in track['artists']],
                                'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
                                'preview_url': track['preview_url'],
                                'external_url': track['external_urls']['spotify'],
                                'id': track['id'],
                                'reason': f"Essential {artist_name} track"
                            })
                            
            # 3. Shuffle and limit
            random.shuffle(recommendations)
            return recommendations[:limit]

        except Exception as e:
            print(f"Error fetching deep cuts: {e}")
            return []
