# musicinsights/services/exportify_parser.py
import csv
from datetime import datetime
from django.utils.text import slugify
from ..models import Upload, Artist, Album, Track, PlaylistEntry

def parse_exportify_file(upload_obj: Upload):
    """
    Detect file type (CSV for now) and parse it.
    """
    file = upload_obj.original_file
    name = file.name.lower()

    if name.endswith('.csv'):
        _parse_csv(upload_obj)
    else:
        # you could raise an error or later support json here
        raise ValueError("Unsupported file type. Please upload a CSV exported from Exportify.")


def _safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def _safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def _parse_csv(upload_obj: Upload):
    """
    Parse an Exportify CSV like the one you sent.
    Expected columns (case-sensitive in your sample):
      - Track URI
      - Track Name
      - Album Name
      - Artist Name(s)
      - Added At
      - Duration (ms)
      - Genres
    Plus other audio features we can ignore for now.
    """
    # we need to reset file pointer to start
    upload_obj.original_file.seek(0)

    # playlist name from filename (Bike_Biking.csv → Bike_Biking)
    raw_name = upload_obj.original_file.name
    playlist_name = raw_name.rsplit('/', 1)[-1].rsplit('\\', 1)[-1].rsplit('.', 1)[0]

    # open as text with fallback encoding
    content = upload_obj.original_file.read()
    try:
        decoded = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        decoded = content.decode('latin-1')
        
    reader = csv.DictReader(decoded.splitlines())

    for row in reader:
        track_uri = row.get('Track URI') or ''
        track_name = row.get('Track Name') or 'Unknown Track'
        album_name = row.get('Album Name') or 'Unknown Album'
        artist_names = row.get('Artist Name(s)') or ''
        added_at_raw = row.get('Added At') or None
        duration_ms = row.get('Duration (ms)') or None
        genres = row.get('Genres') or ''

        # --- artists (can be comma separated)
        artist_objs = []
        if artist_names:
            for artist_name in [a.strip() for a in artist_names.split(';') if a.strip()]:
                # we don't have artist URI in CSV, so we use name as key
                artist_obj, _ = Artist.objects.get_or_create(
                    spotify_id=artist_name,  # using name as id fallback
                    defaults={'name': artist_name}
                )
                artist_objs.append(artist_obj)

        # --- album
        album_obj, _ = Album.objects.get_or_create(
            spotify_id=album_name,  # no album URI, so use name
            defaults={'name': album_name}
        )

        # Audio features
        danceability = row.get('Danceability')
        energy = row.get('Energy')
        valence = row.get('Valence')
        acousticness = row.get('Acousticness')
        instrumentalness = row.get('Instrumentalness')
        liveness = row.get('Liveness')
        speechiness = row.get('Speechiness')
        tempo = row.get('Tempo')
        popularity = row.get('Popularity')
        release_date = row.get('Release Date')

        # --- track
        # track_uri is a good unique key, but if missing, fall back to name + album
        spotify_id = track_uri or f"{track_name}-{album_name}"
        track_obj, _ = Track.objects.get_or_create(
            spotify_id=spotify_id,
            defaults={
                'name': track_name,
                'duration_ms': _safe_int(duration_ms),
                'album': album_obj,
                'genres': genres,
                'danceability': _safe_float(danceability),
                'energy': _safe_float(energy),
                'valence': _safe_float(valence),
                'acousticness': _safe_float(acousticness),
                'instrumentalness': _safe_float(instrumentalness),
                'liveness': _safe_float(liveness),
                'speechiness': _safe_float(speechiness),
                'tempo': _safe_float(tempo),
                'popularity': _safe_int(popularity),
                'release_date': release_date
            }
        )

        # update track if needed
        changed = False
        if track_obj.name != track_name:
            track_obj.name = track_name
            changed = True
        if track_obj.album != album_obj:
            track_obj.album = album_obj
            changed = True
        if genres and track_obj.genres != genres:
            track_obj.genres = genres
            changed = True
        
        # Update audio features if they exist in CSV but not in DB (or changed)
        if danceability and track_obj.danceability != _safe_float(danceability):
            track_obj.danceability = _safe_float(danceability)
            changed = True
        if energy and track_obj.energy != _safe_float(energy):
            track_obj.energy = _safe_float(energy)
            changed = True
        if valence and track_obj.valence != _safe_float(valence):
            track_obj.valence = _safe_float(valence)
            changed = True
        if popularity and track_obj.popularity != _safe_int(popularity):
            track_obj.popularity = _safe_int(popularity)
            changed = True
            
        if changed:
            track_obj.save()

        # set artists m2m
        if artist_objs:
            track_obj.artists.set(artist_objs)

        # --- added_at
        added_at = None
        if added_at_raw:
            # your CSV is like 2025-06-16T20:24:37Z
            try:
                added_at = datetime.fromisoformat(added_at_raw.replace('Z', '+00:00'))
            except ValueError:
                pass

        # create playlist entry
        PlaylistEntry.objects.create(
            upload=upload_obj,
            track=track_obj,
            playlist_name=playlist_name,
            added_at=added_at
        )
