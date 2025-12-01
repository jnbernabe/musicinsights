from django.test import TestCase
from musicinsights.models import Upload, Artist, Album, Track, PlaylistEntry
from musicinsights.services.recommendation_service import build_recommendations
from datetime import datetime

class RecommendationServiceTest(TestCase):
    def setUp(self):
        self.upload = Upload.objects.create()
        self.artist = Artist.objects.create(name="Top Artist", spotify_id="ta1")
        self.album = Album.objects.create(name="Album X", spotify_id="ax1")
        self.track = Track.objects.create(name="Song X", spotify_id="sx1", album=self.album)
        self.track.artists.add(self.artist)

    def test_artist_recommendation(self):
        # Add 5 entries for the same artist to trigger recommendation
        for i in range(5):
            PlaylistEntry.objects.create(
                upload=self.upload,
                track=self.track,
                playlist_name="Playlist",
                added_at=datetime(2023, 1, 1, 12, 0, 0)
            )
            
        recs = build_recommendations(self.upload)
        self.assertTrue(any("Top Artist" in r for r in recs))

    def test_morning_recommendation(self):
        # Add 5 entries in the morning (e.g., 8 AM)
        for i in range(5):
            PlaylistEntry.objects.create(
                upload=self.upload,
                track=self.track,
                playlist_name="Playlist",
                added_at=datetime(2023, 1, 1, 8, 0, 0)
            )
            
        recs = build_recommendations(self.upload)
        self.assertTrue(any("morning" in r for r in recs))

    def test_tempo_recommendation(self):
        # Add high tempo tracks
        for i in range(5):
            t = Track.objects.create(name=f"Fast Song {i}", spotify_id=f"fs{i}", tempo=150)
            PlaylistEntry.objects.create(
                upload=self.upload,
                track=t,
                playlist_name="Workout",
                added_at=datetime(2023, 1, 1, 12, 0, 0)
            )
            
        recs = build_recommendations(self.upload)
        self.assertTrue(any("High Tempo" in r for r in recs))
