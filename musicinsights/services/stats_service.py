from collections import Counter
import json
from datetime import datetime
from ..models import PlaylistEntry

def build_dashboard_context(upload):
    entries = PlaylistEntry.objects.filter(upload=upload).select_related('track', 'track__album')
    total_tracks = entries.count()

    artist_counter = Counter()
    track_listening_time = Counter()
    monthly_listening_time = Counter()

    # --- Audio Features Averages ---
    features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    feature_totals = {f: 0.0 for f in features}
    feature_counts = {f: 0 for f in features}
    
    # --- Genre Counting ---
    genre_counter = Counter()

    # Total listening time
    total_listening_time_ms = 0

    # --- New Metrics Initialization ---
    time_of_day_counts = {'Morning': 0, 'Afternoon': 0, 'Evening': 0, 'Night': 0}
    era_counts = Counter()
    popularity_counts = { '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0 }
    tempo_counts = { '<80 BPM': 0, '80-100 BPM': 0, '100-120 BPM': 0, '120-140 BPM': 0, '>140 BPM': 0 }

    for e in entries:
        track = e.track
        duration_ms = track.duration_ms or 0
        
        for artist in track.artists.all():
            artist_counter[artist.name] += 1

        # Count by track object and accumulate listening time
        track_listening_time[track] += duration_ms
        
        total_listening_time_ms += duration_ms

        if e.added_at:
            key = e.added_at.strftime('%Y-%m')
            monthly_listening_time[key] += duration_ms
            
            # Time of Day
            h = e.added_at.hour
            if 5 <= h <= 11: time_of_day_counts['Morning'] += 1
            elif 12 <= h <= 17: time_of_day_counts['Afternoon'] += 1
            elif 18 <= h <= 23: time_of_day_counts['Evening'] += 1
            else: time_of_day_counts['Night'] += 1

        # Music Era
        if track.release_date:
            try:
                year = int(track.release_date[:4])
                decade = f"{(year // 10) * 10}s"
                era_counts[decade] += 1
            except (ValueError, TypeError):
                pass

        # Popularity
        if track.popularity is not None:
            pop = track.popularity
            if pop <= 20: popularity_counts['0-20'] += 1
            elif pop <= 40: popularity_counts['21-40'] += 1
            elif pop <= 60: popularity_counts['41-60'] += 1
            elif pop <= 80: popularity_counts['61-80'] += 1
            else: popularity_counts['81-100'] += 1

        # Tempo
        if track.tempo:
            bpm = track.tempo
            if bpm < 80: tempo_counts['<80 BPM'] += 1
            elif bpm < 100: tempo_counts['80-100 BPM'] += 1
            elif bpm < 120: tempo_counts['100-120 BPM'] += 1
            elif bpm < 140: tempo_counts['120-140 BPM'] += 1
            else: tempo_counts['>140 BPM'] += 1
            
        # Audio features
        for f in features:
            val = getattr(track, f, None)
            if val is not None:
                feature_totals[f] += val
                feature_counts[f] += 1
        
        # Genres (comma separated in DB)
from collections import Counter
import json
from datetime import datetime
from ..models import PlaylistEntry

def build_dashboard_context(upload):
    entries = PlaylistEntry.objects.filter(upload=upload).select_related('track', 'track__album')
    total_tracks = entries.count()

    artist_counter = Counter()
    track_listening_time = Counter()
    monthly_listening_time = Counter()

    # --- Audio Features Averages ---
    features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    feature_totals = {f: 0.0 for f in features}
    feature_counts = {f: 0 for f in features}
    
    # --- Genre Counting ---
    genre_counter = Counter()

    # Total listening time
    total_listening_time_ms = 0

    # --- New Metrics Initialization ---
    time_of_day_counts = {'Morning': 0, 'Afternoon': 0, 'Evening': 0, 'Night': 0}
    era_counts = Counter()
    popularity_counts = { '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0 }
    tempo_counts = { '<80 BPM': 0, '80-100 BPM': 0, '100-120 BPM': 0, '120-140 BPM': 0, '>140 BPM': 0 }

    for e in entries:
        track = e.track
        duration_ms = track.duration_ms or 0
        
        for artist in track.artists.all():
            artist_counter[artist.name] += 1

        # Count by track object and accumulate listening time
        track_listening_time[track] += duration_ms
        
        total_listening_time_ms += duration_ms

        if e.added_at:
            key = e.added_at.strftime('%Y-%m')
            monthly_listening_time[key] += duration_ms
            
            # Time of Day
            h = e.added_at.hour
            if 5 <= h <= 11: time_of_day_counts['Morning'] += 1
            elif 12 <= h <= 17: time_of_day_counts['Afternoon'] += 1
            elif 18 <= h <= 23: time_of_day_counts['Evening'] += 1
            else: time_of_day_counts['Night'] += 1

        # Music Era
        if track.release_date:
            try:
                year = int(track.release_date[:4])
                decade = f"{(year // 10) * 10}s"
                era_counts[decade] += 1
            except (ValueError, TypeError):
                pass

        # Popularity
        if track.popularity is not None:
            pop = track.popularity
            if pop <= 20: popularity_counts['0-20'] += 1
            elif pop <= 40: popularity_counts['21-40'] += 1
            elif pop <= 60: popularity_counts['41-60'] += 1
            elif pop <= 80: popularity_counts['61-80'] += 1
            else: popularity_counts['81-100'] += 1

        # Tempo
        if track.tempo:
            bpm = track.tempo
            if bpm < 80: tempo_counts['<80 BPM'] += 1
            elif bpm < 100: tempo_counts['80-100 BPM'] += 1
            elif bpm < 120: tempo_counts['100-120 BPM'] += 1
            elif bpm < 140: tempo_counts['120-140 BPM'] += 1
            else: tempo_counts['>140 BPM'] += 1
            
        # Audio features
        for f in features:
            val = getattr(track, f, None)
            if val is not None:
                feature_totals[f] += val
                feature_counts[f] += 1
        
        # Genres (comma separated in DB)
        if track.genres:
            for g in track.genres.split(','):
                g_clean = g.strip()
                if g_clean:
                    genre_counter[g_clean] += 1

    # --- Top Artists by Duration ---
    artist_duration = Counter()
    for track, duration_ms in track_listening_time.items():
        for artist in track.artists.all():
            artist_duration[artist.name] += duration_ms

    # Get top 10 artists by duration
    top_artists_duration = artist_duration.most_common(10)
    top_artists_duration_labels = [a[0] for a in top_artists_duration]
    # Convert to hours
    top_artists_duration_values = [round(a[1] / (1000 * 60 * 60), 2) for a in top_artists_duration]

    # Calculate averages
    avg_features = []
    for f in features:
        if feature_counts[f] > 0:
            avg_features.append(round(feature_totals[f] / feature_counts[f], 3))
        else:
            avg_features.append(0)

    # Convert total listening time to hours
    total_listening_hours = round(total_listening_time_ms / (1000 * 60 * 60), 3)

    first_entry = entries.first()
    playlist_name = first_entry.playlist_name if first_entry else "Unknown Playlist"

    # Prepare Era Data (Sorted)
    sorted_eras = sorted(era_counts.keys())
    era_values = [era_counts[e] for e in sorted_eras]

    return {
        "playlist_name": playlist_name,
        "total_tracks": total_tracks,
        "total_listening_hours": total_listening_hours,
        "top_artists": artist_counter.most_common(10),
        "top_tracks": [
            {
                'name': t.name,
                'artist': ", ".join([a.name for a in t.artists.all()]),
                'album': t.album.name if t.album else 'Unknown',
                'listening_time_hours': round(time_ms / (1000 * 60 * 60), 2)
            }
            for t, time_ms in track_listening_time.most_common(10)
        ],
        # Replaced Monthly Data with Top Artists Duration
        "top_artists_duration_labels": json.dumps(top_artists_duration_labels),
        "top_artists_duration_values": json.dumps(top_artists_duration_values),
        
        "avg_features": json.dumps(avg_features),
        "feature_labels": json.dumps([f.capitalize() for f in features]),
        "top_genres": json.dumps(genre_counter.most_common(10)),
        "genre_labels": json.dumps([g[0] for g in genre_counter.most_common(10)]),
        "genre_values": json.dumps([g[1] for g in genre_counter.most_common(10)]),
        
        # New Data
        "time_of_day_labels": json.dumps(list(time_of_day_counts.keys())),
        "time_of_day_values": json.dumps(list(time_of_day_counts.values())),
        "era_labels": json.dumps(sorted_eras),
        "era_values": json.dumps(era_values),
        "popularity_labels": json.dumps(list(popularity_counts.keys())),
        "popularity_values": json.dumps(list(popularity_counts.values())),
        "tempo_labels": json.dumps(list(tempo_counts.keys())),
        "tempo_values": json.dumps(list(tempo_counts.values())),
        
        # Mood Map Data (Scatter Plot)
        "mood_data": json.dumps([
            {'x': t.valence, 'y': t.energy, 'name': t.name, 'artist': t.artists.first().name if t.artists.exists() else 'Unknown'}
            for t in track_listening_time.keys()
            if t.valence is not None and t.energy is not None
        ]),
    }