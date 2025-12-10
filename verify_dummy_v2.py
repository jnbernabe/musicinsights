
import sys
import os
from datetime import datetime

sys.path.append(os.getcwd())

try:
    from musicinsights.services.dummy_data_service import generate_dummy_data
    
    data = generate_dummy_data()
    print(f"Generated {len(data)} items.")
    
    # Check genres
    multi_genre_count = 0
    for item in data:
        genres = item['track']['genres']
        if len(genres) > 1:
            multi_genre_count += 1
    
    print(f"Tracks with multiple genres: {multi_genre_count}")
    if multi_genre_count == 0:
        print("FAILURE: No tracks with multiple genres.")
        sys.exit(1)
        
    # Check dates
    years = set()
    for item in data:
        date_str = item['track']['release_date']
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        years.add(dt.year)
        
    print(f"Years covered: {sorted(list(years))}")
    if len(years) < 10:
        print("FAILURE: Date range too narrow.")
        sys.exit(1)
            
    print("SUCCESS: Data improvements verified.")

except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
