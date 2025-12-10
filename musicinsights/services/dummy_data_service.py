import random
from datetime import datetime, timedelta

def generate_dummy_data():
    """
    Generates a list of dummy track entries mimicking the structure of parsed Exportify CSV data.
    """
    
    genres_list = ['Pop', 'Rock', 'Hip Hop', 'Jazz', 'Electronic', 'Classical', 'Indie', 'R&B']
    artists_pool = [
        'The Cosmic Rays', 'Lunar Echoes', 'Neon Pulse', 'Velvet Shadows', 
        'Crystal Tides', 'Retro Wave', 'Midnight Drivers', 'Solar Flares',
        'Quantum Beats', 'Stellar Drifters'
    ]
    albums_pool = [
        'First Contact', 'Dark Side of the Moon Base', 'Electric Dreams', 
        'Neon Nights', 'Future Nostalgia', 'Retrograde', 'Stardust', 'Gravity'
    ]
    
    tracks = []
    base_date = datetime.now()
    
    for i in range(50):
        # Weighted random selection for more realistic distribution
        # Select 1-3 genres
        num_genres = random.randint(1, 3)
        track_genres = random.sample(genres_list, k=num_genres)
        primary_genre = track_genres[0] # Used for feature correlation
        
        artist = random.choice(artists_pool)
        album = random.choice(albums_pool)
        
        # Correlate features slightly with genre for semi-realism
        if primary_genre in ['Electronic', 'Pop', 'Hip Hop']:
            energy = random.uniform(0.6, 0.95)
            danceability = random.uniform(0.6, 0.9)
            acousticness = random.uniform(0.0, 0.3)
        elif primary_genre in ['Classical', 'Jazz']:
            energy = random.uniform(0.1, 0.5)
            danceability = random.uniform(0.2, 0.5)
            acousticness = random.uniform(0.7, 1.0)
        else:
            energy = random.uniform(0.3, 0.8)
            danceability = random.uniform(0.3, 0.7)
            acousticness = random.uniform(0.1, 0.6)

        track = {
            'track': {
                'name': f'Track {i+1} - {primary_genre} Vibes',
                'artists': [artist],
                'album': album,
                'duration_ms': random.randint(120000, 300000), # 2-5 minutes
                'genres': track_genres,
                'uri': f'spotify:track:dummy{i}',
                'danceability': danceability,
                'energy': energy,
                'valence': random.uniform(0.1, 0.9),
                'acousticness': acousticness,
                'instrumentalness': random.uniform(0, 0.8) if primary_genre in ['Electronic', 'Classical'] else random.uniform(0, 0.1),
                'liveness': random.uniform(0.05, 0.3),
                'speechiness': random.uniform(0.03, 0.2),
                'tempo': random.uniform(60, 180),
                'popularity': random.randint(20, 90),
                'release_date': (base_date - timedelta(days=random.randint(0, 18000))).strftime('%Y-%m-%d')
            },
            'added_at': (base_date - timedelta(days=random.randint(0, 365))).isoformat(),
            'playlist_name': 'Demo Playlist'
        }
        tracks.append(track)
        
    return tracks
