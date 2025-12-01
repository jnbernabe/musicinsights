from collections import Counter
from ..models import PlaylistEntry

def build_dashboard_context(upload):
    entries = PlaylistEntry.objects.filter(upload=upload).select_related('track', 'track__album')
    total_tracks = entries.count()

    artist_counter = Counter()
    track_listening_time = Counter()  # Changed to track listening time
    monthly_listening_time = Counter()  # Changed to listening time

    # --- Audio Features Averages ---
    features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    feature_totals = {f: 0.0 for f in features}
    feature_counts = {f: 0 for f in features}
    
    # --- Genre Counting ---
    genre_counter = Counter()

    # Total listening time
    total_listening_time_ms = 0

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

    monthly_labels = sorted(monthly_listening_time.keys())
    # Convert milliseconds to hours for display
    monthly_values = [round(monthly_listening_time[m] / (1000 * 60 * 60), 2) for m in monthly_labels]

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
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "avg_features": avg_features,
        "feature_labels": [f.capitalize() for f in features],
        "top_genres": genre_counter.most_common(10),
        "genre_labels": [g[0] for g in genre_counter.most_common(10)],
        "genre_values": [g[1] for g in genre_counter.most_common(10)],
    }