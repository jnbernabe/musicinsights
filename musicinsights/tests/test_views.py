from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from musicinsights.models import Upload

class UploadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('upload_file')

    def test_upload_valid_csv(self):
        csv_content = b"Track URI,Track Name,Album Name,Artist Name(s)\nspotify:track:1,Song A,Album A,Artist A"
        file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        self.assertEqual(Upload.objects.count(), 1)

    def test_upload_invalid_file_type(self):
        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        
        response = self.client.post(self.upload_url, {'file': file})
        
        self.assertEqual(response.status_code, 200) # Renders upload page with error
        self.assertContains(response, "Unsupported file type")
