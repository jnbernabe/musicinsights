
import sys
import os

sys.path.append(os.getcwd())
# Mock settings if needed for imports, but the service only uses random/datetime
try:
    from musicinsights.services.dummy_data_service import generate_dummy_data
    
    data = generate_dummy_data()
    print(f"Generated {len(data)} items.")
    first = data[0]
    print(f"Sample item keys: {first.keys()}")
    print(f"Sample track keys: {first['track'].keys()}")
    
    required_keys = ['danceability', 'energy', 'tempo']
    for key in required_keys:
        if key not in first['track']:
            print(f"MISSING KEY: {key}")
            sys.exit(1)
            
    print("SUCCESS: Data structure looks correct.")

except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
