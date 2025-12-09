from collections import Counter
import json
from datetime import datetime

def build_dashboard_context(playlist_data, playlist_name_override=None):
    entries = playlist_data
    total_tracks = len(entries)

    artist_counter = Counter()
    track_listening_time = Counter() # Key: (track_name, artist_name), Value: duration
    track_objects = {} # Key: (track_name, artist_name), Value: track dict
    
    # monthly_listening_time = Counter() # Removed as per previous changes

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
    
    all_tracks_serialized = [] # For frontend JS filtering

    for e in entries:
        track = e['track']
        duration_ms = track.get('duration_ms') or 0
        
        # Track Key for aggregation
        track_key = (track['name'], ", ".join(track['artists']))
        track_objects[track_key] = track
        
        for artist_name in track['artists']:
            artist_counter[artist_name] += 1

        # Count by track object and accumulate listening time
        track_listening_time[track_key] += duration_ms
        
        total_listening_time_ms += duration_ms

        added_at_str = e.get('added_at')
        if added_at_str:
            # Parse ISO string
            try:
                if 'T' in added_at_str:
                     dt = datetime.fromisoformat(added_at_str.replace('Z', '+00:00'))
                else:
                     dt = None
                
                if dt:
                    # Time of Day
                    h = dt.hour
                    if 5 <= h <= 11: time_str = 'Morning'
                    elif 12 <= h <= 17: time_str = 'Afternoon'
                    elif 18 <= h <= 23: time_str = 'Evening'
                    else: time_str = 'Night'
                    
                    time_of_day_counts[time_str] += 1
            except ValueError:
                time_str = None
                pass
        else:
            time_str = None

        # Music Era
        release_date = track.get('release_date')
        era_str = None
        if release_date:
            try:
                year = int(release_date[:4])
                era_str = f"{(year // 10) * 10}s"
                era_counts[era_str] += 1
            except (ValueError, TypeError):
                pass

        # Popularity
        pop = track.get('popularity')
        pop_str = None
        if pop is not None:
            if pop <= 20: pop_str = '0-20'
            elif pop <= 40: pop_str = '21-40'
            elif pop <= 60: pop_str = '41-60'
            elif pop <= 80: pop_str = '61-80'
            else: pop_str = '81-100'
            popularity_counts[pop_str] += 1

        # Tempo
        bpm = track.get('tempo')
        tempo_str = None
        if bpm:
            if bpm < 80: tempo_str = '<80 BPM'
            elif bpm < 100: tempo_str = '80-100 BPM'
            elif bpm < 120: tempo_str = '100-120 BPM'
            elif bpm < 140: tempo_str = '120-140 BPM'
            else: tempo_str = '>140 BPM'
            tempo_counts[tempo_str] += 1
            
        # Audio features
        for f in features:
            val = track.get(f)
            if val is not None:
                feature_totals[f] += val
                feature_counts[f] += 1
        
        # Genres
        track_genres = track.get('genres', [])
        for g in track_genres:
            genre_counter[g] += 1

        # --- Serialize for JS ---
        # We need to construct a clean object for the frontend filter
        track_obj = {
            'name': track['name'],
            'artist': ", ".join(track['artists']),
            'album': track['album'],
            'listening_time_hours': round(duration_ms / (1000 * 60 * 60), 3),
            'duration_ms': duration_ms, # Needed for aggregation
            'era': era_str,
            'time_of_day': time_str,
            'popularity_bucket': pop_str,
            'tempo_bucket': tempo_str,
            'genres': track_genres,
            'url': track.get('external_urls', {}).get('spotify', '#')
        }
        
        # Add audio features
        for f in features:
            track_obj[f] = track.get(f)
            
        all_tracks_serialized.append(track_obj)

    # --- Top Artists by Duration ---
    artist_duration = Counter()
    for track_key, duration_ms in track_listening_time.items():
        track = track_objects[track_key]
        for artist_name in track['artists']:
            artist_duration[artist_name] += duration_ms

    # Get top 10 artists by duration
    top_artists_duration = artist_duration.most_common(10)
    top_artists_duration_labels = [x[0] for x in top_artists_duration]
    top_artists_duration_values = [round(x[1] / (1000 * 60), 1) for x in top_artists_duration]

    # Calculate averages
    avg_features = []
    for f in features:
        if feature_counts[f] > 0:
            avg_features.append(round(feature_totals[f] / feature_counts[f], 3))
        else:
            avg_features.append(0)

    # Convert total listening time to hours
    total_listening_hours = round(total_listening_time_ms / (1000 * 60 * 60), 3)

    if playlist_name_override:
        playlist_name = playlist_name_override
    else:
        playlist_name = entries[0]['playlist_name'] if entries else "Unknown Playlist"

    # Prepare Era Data (Sorted)
    sorted_eras = sorted(era_counts.keys())
    era_values = [era_counts[e] for e in sorted_eras]
    
    # Top Tracks
    top_tracks_data = []
    for track_key, time_ms in track_listening_time.items():
        track = track_objects[track_key]
        top_tracks_data.append({
            'name': track['name'],
            'artist': ", ".join(track['artists']),
            'album': track['album'],
            'listening_time_hours': round(time_ms / (1000 * 60 * 60), 2)
        })

    # Mood Data
    mood_data = []
    for track_key in track_listening_time.keys():
        track = track_objects[track_key]
        valence = track.get('valence')
        energy = track.get('energy')
        if valence is not None and energy is not None:
             mood_data.append({
                 'x': valence,
                 'y': energy,
                 'name': track['name'],
                 'artist': track['artists'][0] if track['artists'] else 'Unknown'
             })

    # Vibe Calculation
    vibe = determine_playlist_vibe(avg_features, feature_labels=features)

    # Text Insights Generation
    insights_list = generate_text_insights(
        total_tracks=total_tracks,
        artist_counter=artist_counter,
        genre_counter=genre_counter,
        era_counts=era_counts,
        popularity_counts=popularity_counts,
        tempo_counts=tempo_counts,
        avg_features_values=avg_features,
        feature_labels=features,
        time_of_day_counts=time_of_day_counts
    )

    return {
        "playlist_name": playlist_name,
        "playlist_vibe": vibe,
        "text_insights": insights_list,
        "total_tracks": total_tracks,
        "total_listening_hours": total_listening_hours,
        "top_artists": artist_counter.most_common(10),
        "top_tracks": top_tracks_data,
        
        "top_artists_duration_labels": json.dumps(top_artists_duration_labels),
        "top_artists_duration_values": json.dumps(top_artists_duration_values),
        
        "avg_features": json.dumps(avg_features),
        "feature_labels": json.dumps([f.capitalize() for f in features]),
        "top_genres": json.dumps(genre_counter.most_common(10)),
        "genre_labels": json.dumps([g[0] for g in genre_counter.most_common(10)]),
        "genre_values": json.dumps([g[1] for g in genre_counter.most_common(10)]),
        
        "time_of_day_labels": json.dumps(list(time_of_day_counts.keys())),
        "time_of_day_values": json.dumps(list(time_of_day_counts.values())),
        "era_labels": json.dumps(sorted_eras),
        "era_values": json.dumps(era_values),
        "popularity_labels": json.dumps(list(popularity_counts.keys())),
        "popularity_values": json.dumps(list(popularity_counts.values())),
        "tempo_labels": json.dumps(list(tempo_counts.keys())),
        "tempo_values": json.dumps(list(tempo_counts.values())),
        
        "tempo_values": json.dumps(list(tempo_counts.values())),
        
        "mood_data": json.dumps(mood_data),
        
        "all_tracks_json": json.dumps(all_tracks_serialized),
    }

def generate_text_insights(total_tracks, artist_counter, genre_counter, era_counts, popularity_counts, tempo_counts, avg_features_values, feature_labels, time_of_day_counts):
    insights = []
    
    if total_tracks == 0:
        return ["Not enough data for insights."]

    # 1. Top Artist (Always show top)
    if artist_counter:
        top_artist, count = artist_counter.most_common(1)[0]
        percent = (count / total_tracks) * 100
        if percent > 20:
            insights.append(f"You're a super-fan of <strong>{top_artist}</strong> ({int(percent)}% of playlist).")
        elif percent > 5:
             insights.append(f"<strong>{top_artist}</strong> is your top artist here.")

    # 2. Genre (Always show top)
    if genre_counter:
        top_genre, count = genre_counter.most_common(1)[0]
        percent = (count / total_tracks) * 100
        if percent > 40:
             insights.append(f"This playlist is heavily <strong>{top_genre}</strong> focused ({int(percent)}%).")
        else:
             insights.append(f"Your top genre is <strong>{top_genre}</strong> ({int(percent)}%).")

    # 3. Era Analysis
    if era_counts:
        dominant_era = era_counts.most_common(1)[0]
        era_name, count = dominant_era
        percent = (count / total_tracks) * 100
        if percent > 50:
             insights.append(f"You are stuck in the <strong>{era_name}</strong>.")
        else:
             insights.append(f"Most tracks ({int(percent)}%) are from the <strong>{era_name}</strong>.")

    # 4. Popularity
    obscure_count = popularity_counts.get('0-20', 0)
    mainstream_count = popularity_counts.get('81-100', 0)
    
    if obscure_count > (total_tracks * 0.3):
        insights.append("You have a <strong>Deep / Underground</strong> taste.")
    elif mainstream_count > (total_tracks * 0.5):
        insights.append("You love <strong>Mainstream Hits</strong>.")

    # 5. Tempo
    high_tempo = tempo_counts.get('>140 BPM', 0)
    low_tempo = tempo_counts.get('<80 BPM', 0)
    
    if high_tempo > (total_tracks * 0.3):
        insights.append("You prefer <strong>High Energy / Fast</strong> tempos.")
    elif low_tempo > (total_tracks * 0.3):
         insights.append("You like it <strong>Slow & Steady</strong>.")

    # 6. Mood (Valence)
    feats = dict(zip(feature_labels, avg_features_values))
    valence = feats.get('valence', 0)
    energy = feats.get('energy', 0)

    if valence > 0.65:
        insights.append("Overall mood is <strong>Positive & Cheerful</strong>.")
    elif valence < 0.4:
        insights.append("Overall mood is quite <strong>Melancholy</strong>.")
    
    if energy > 0.7:
        insights.append("This is a <strong>High Energy</strong> playlist.")



    # Limit to 8
    return insights[:7]

def determine_playlist_vibe(avg_features_values, feature_labels):
    """
    Heuristic to determine the 'Vibe' of the playlist based on average audio features.
    """
    # Map features to values for easier access
    feats = dict(zip(feature_labels, avg_features_values))
    
    energy = feats.get('energy', 0)
    valence = feats.get('valence', 0)
    danceability = feats.get('danceability', 0)
    acousticness = feats.get('acousticness', 0)
    tempo = feats.get('tempo', 0) # Note: Average tempo might not be normalized 0-1, usually raw BPM. 
    # Actually build_context averages raw values. Tempo is commonly 0-200+.
    # We should handle tempo carefully or ignore it if 'avg_features' includes it as raw number.
    # Looking at build_dashboard_context, 'tempo' is in features list? 
    # Yes: features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    # Wait, 'tempo' isn't in that list! 
    # In Step 222: features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']
    # So 'tempo' is NOT in avg_features. Good to know.
    
    # Logic Tree
    if energy > 0.75 and valence > 0.6:
        return "High Voltage Party ⚡"
    elif energy > 0.7 and danceability > 0.7:
        return "Club / Dancefloor 💃"
    elif energy > 0.8:
        return "Workout / Pump Up 💪"
    elif energy < 0.4 and valence < 0.35:
        return "Melancholy / Sad Boi 🌧️"
    elif acousticness > 0.7 and energy < 0.5:
        return "Coffee Shop / Acoustic ☕"
    elif energy < 0.55 and valence > 0.6:
        return "Chill / Good Vibes 🌅"
    elif danceability > 0.75:
        return "Groovy / Funky 🕺"
    elif feats.get('instrumentalness', 0) > 0.5:
        return "Focus / Study 🧠"
    elif energy > 0.6 and valence < 0.4:
        return "Moody / Dark 🌑"
    else:
        return "Eclectic Mix 🎧"