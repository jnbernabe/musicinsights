from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from musicinsights.models import Upload
from musicinsights.services.exportify_parser import parse_exportify_file

class ParserErrorTest(TestCase):
    def test_latin1_encoding(self):
        # Create a CSV with latin-1 characters that are invalid in UTF-8
        # \xe9 is 'é' in latin-1
        content = b"Track URI,Track Name,Album Name,Artist Name(s)\nspotify:track:1,Song \xe9,Album A,Artist A"
        file = SimpleUploadedFile("latin1.csv", content, content_type="text/csv")
        upload = Upload.objects.create(original_file=file)
        
    def test_latin1_encoding(self):
        # Create a CSV with latin-1 characters that are invalid in UTF-8
        # \xe9 is 'é' in latin-1
        content = b"Track URI,Track Name,Album Name,Artist Name(s)\nspotify:track:1,Song \xe9,Album A,Artist A"
        file = SimpleUploadedFile("latin1.csv", content, content_type="text/csv")
        upload = Upload.objects.create(original_file=file)
        
        # This should now succeed
        parse_exportify_file(upload)
        
        # Verify the track was created with the correct name
        # In latin-1, \xe9 is é. If we decode as latin-1, we get é.
        from musicinsights.models import Track
        self.assertTrue(Track.objects.filter(name="Song é").exists())

    def test_invalid_number_format(self):
        content = (
            "Track URI,Track Name,Album Name,Artist Name(s),Duration (ms),Danceability\n"
            "spotify:track:1,Song A,Album A,Artist A,invalid_int,invalid_float"
        ).encode('utf-8')
        file = SimpleUploadedFile("invalid_numbers.csv", content, content_type="text/csv")
        upload = Upload.objects.create(original_file=file)
        
        # This should now succeed (gracefully handle invalid numbers)
        parse_exportify_file(upload)
        
        from musicinsights.models import Track
        track = Track.objects.get(spotify_id="spotify:track:1")
        self.assertIsNone(track.duration_ms)
        self.assertIsNone(track.danceability)
