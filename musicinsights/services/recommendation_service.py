from collections import Counter
from ..models import PlaylistEntry

def build_recommendations(upload):
    entries = PlaylistEntry.objects.filter(upload=upload).select_related('track')
    artist_counter = Counter()
    genre_counter = Counter()
    time_of_day_counter = Counter()
    total_listening_time_ms = 0
    track_count = entries.count()

    for e in entries:
        track = e.track
        duration_ms = track.duration_ms or 0
        total_listening_time_ms += duration_ms
        
        for artist in track.artists.all():
            artist_counter[artist.name] += 1
            
        if track.genres:
            for g in track.genres.split(','):
                g_clean = g.strip()
                if g_clean:
                    genre_counter[g_clean] += 1
                    
        if e.added_at:
            time_of_day_counter[e.added_at.hour] += 1

    recs = []

    # Total listening time recommendation
    total_hours = round(total_listening_time_ms / (1000 * 60 * 60), 1)
    if total_hours > 10:
        recs.append(f"🎵 You've listened to {total_hours} hours of music! That's dedication to your craft.")
    
    # Top artist recommendation
    if artist_counter:
        top_artist, top_count = artist_counter.most_common(1)[0]
        percentage = round((top_count / track_count) * 100, 1)
        if percentage >= 15:
            recs.append(f"🎤 {top_artist} makes up {percentage}% of your library. Consider exploring their deep cuts and B-sides.")
        elif top_count >= 5:
            recs.append(f"🎸 You're a fan of {top_artist}. Check out similar artists in the same genre.")
    
    # Genre diversity recommendation
    if genre_counter:
        top_genre, genre_count = genre_counter.most_common(1)[0]
        total_genres = len(genre_counter)
        if total_genres >= 10:
            recs.append(f"🌈 You have {total_genres} different genres! Your taste is wonderfully eclectic.")
        elif total_genres <= 3:
            recs.append(f"🎯 Your music is focused on {top_genre}. Try branching out to discover new sounds.")
    
    # Time of day patterns
    morning_adds = sum(cnt for h, cnt in time_of_day_counter.items() if 5 <= h <= 11)
    afternoon_adds = sum(cnt for h, cnt in time_of_day_counter.items() if 12 <= h <= 17)
    evening_adds = sum(cnt for h, cnt in time_of_day_counter.items() if 18 <= h <= 23)
    night_adds = sum(cnt for h, cnt in time_of_day_counter.items() if 0 <= h <= 4)
    
    max_time = max(morning_adds, afternoon_adds, evening_adds, night_adds)
    if max_time == morning_adds and morning_adds >= 5:
        recs.append("☀️ You're a morning music curator! Create an energizing wake-up playlist.")
    elif max_time == evening_adds and evening_adds >= 5:
        recs.append("🌙 Evening is your music discovery time. Perfect for unwinding with new finds.")
    elif max_time == night_adds and night_adds >= 5:
        recs.append("🌃 Late night listener! Your nocturnal sessions deserve a dedicated chill playlist.")
    
    # Energy-based recommendation (if we have audio features)
    high_energy_tracks = sum(1 for e in entries if e.track.energy and e.track.energy > 0.7)
    if high_energy_tracks > track_count * 0.6:
        recs.append("⚡ Your library is high-energy! Balance it out with some mellow tracks for variety.")
    elif high_energy_tracks < track_count * 0.3:
        recs.append("😌 You prefer chill vibes. Add some upbeat tracks for when you need a boost.")

    # Tempo-based recommendation
    total_tempo = sum(e.track.tempo for e in entries if e.track.tempo)
    avg_tempo = total_tempo / track_count if track_count > 0 else 0
    if avg_tempo > 120:
        recs.append("🏃‍♂️ High Tempo! Great for workouts.")
    
    # Fallback if no recommendations
    if not recs:
        recs.append("🎧 Keep exploring music! Your library is growing.")
    
    return recs
