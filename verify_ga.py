
import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.getcwd())

# Set env var for testing
os.environ['GOOGLE_ANALYTICS_ID'] = 'TEST_ID'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicdata.settings')

try:
    django.setup()
    from musicinsights.context_processors import google_analytics
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get('/')
    
    # Test context processor
    context = google_analytics(request)
    if context.get('GOOGLE_ANALYTICS_ID') == 'TEST_ID':
        print("SUCCESS: Context processor returned correct ID")
    else:
        print(f"FAILURE: Context processor returned {context}")
        sys.exit(1)

    # Validate settings load
    from django.conf import settings
    if settings.GOOGLE_ANALYTICS_ID == 'TEST_ID':
        print("SUCCESS: Settings loaded ID from env")
    else:
        print(f"FAILURE: Settings has {settings.GOOGLE_ANALYTICS_ID}")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
