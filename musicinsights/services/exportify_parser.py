# musicinsights/services/exportify_parser.py
import csv
from datetime import datetime

def parse_exportify_csv(file_content, file_name):
    """
    Parse an Exportify CSV content and return a list of dicts.
    Expected columns:
      - Track URI
      - Track Name
      - Album Name
      - Artist Name(s)
      - Added At
      - Duration (ms)
      - Genres
      - Audio Features...
    """
    # Playlist name from filename
    playlist_name = file_name.rsplit('/', 1)[-1].rsplit('\\', 1)[-1].rsplit('.', 1)[0]

    # Decode content
    try:
        decoded = file_content.decode('utf-8-sig')
    except UnicodeDecodeError:
        decoded = file_content.decode('latin-1')
        
    reader = csv.DictReader(decoded.splitlines())
    
    entries = []

    for row in reader:
        track_uri = row.get('Track URI') or ''
        track_name = row.get('Track Name') or 'Unknown Track'
        album_name = row.get('Album Name') or 'Unknown Album'
        artist_names = row.get('Artist Name(s)') or ''
        added_at_raw = row.get('Added At') or None
        duration_ms = _safe_int(row.get('Duration (ms)'))
        genres = row.get('Genres') or ''

        # Parse artists
        artists = [a.strip() for a in artist_names.split(';') if a.strip()]

        # Audio features
        audio_features = {
            'danceability': _safe_float(row.get('Danceability')),
            'energy': _safe_float(row.get('Energy')),
            'valence': _safe_float(row.get('Valence')),
            'acousticness': _safe_float(row.get('Acousticness')),
            'instrumentalness': _safe_float(row.get('Instrumentalness')),
            'liveness': _safe_float(row.get('Liveness')),
            'speechiness': _safe_float(row.get('Speechiness')),
            'tempo': _safe_float(row.get('Tempo')),
            'popularity': _safe_int(row.get('Popularity')),
            'release_date': row.get('Release Date')
        }

        # Added At
        added_at = None
        if added_at_raw:
            try:
                # Keep as string for JSON serialization, or ISO format
                # datetime.fromisoformat(added_at_raw.replace('Z', '+00:00'))
                added_at = added_at_raw # Keep raw string, parse later if needed or ensure it's ISO
            except ValueError:
                pass

        entry = {
            'track': {
                'name': track_name,
                'artists': artists,
                'album': album_name,
                'duration_ms': duration_ms,
                'genres': [g.strip() for g in genres.split(',') if g.strip()],
                'uri': track_uri,
                **audio_features
            },
            'added_at': added_at,
            'playlist_name': playlist_name
        }
        entries.append(entry)

    return entries

def _safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def _safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
