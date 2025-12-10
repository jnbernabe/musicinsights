from django.shortcuts import render, redirect
import uuid
from datetime import datetime
from .services.exportify_parser import parse_exportify_csv
from .services.stats_service import build_dashboard_context
from django.conf import settings
from .services.recommendation_service import build_recommendations
from .services.spotify_service import SpotifyService
from .services.dummy_data_service import generate_dummy_data
import os

def get_spotify_service(request):
    # Use server-side credentials
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    
    if client_id and client_secret:
        return SpotifyService(client_id, client_secret)
    return None

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            # Read file content into memory
            content = file.read()
            # Parse CSV
            playlist_data = parse_exportify_csv(content, file.name)
            
            # Generate ID
            playlist_id = str(uuid.uuid4())
            
            # Handle duplicate names
            history = request.session.get('history', [])
            base_name = file.name
            display_name = base_name
            counter = 1
            
            existing_names = [p['name'] for p in history]
            while display_name in existing_names:
                name_parts = base_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    display_name = f"{name_parts[0]} ({counter}).{name_parts[1]}"
                else:
                    display_name = f"{base_name} ({counter})"
                counter += 1
            
            playlist_obj = {
                'id': playlist_id,
                'name': display_name,
                'data': playlist_data,
                'created_at': datetime.now().isoformat()
            }
            
            # Store in session history
            history.append(playlist_obj)
            request.session['history'] = history
            
            return redirect('dashboard', playlist_id=playlist_id)
        except ValueError as e:
            return render(request, 'musicinsights/upload.html', {'error': str(e)})
    return render(request, 'musicinsights/upload.html')

def load_dummy_data(request):
    """Generates dummy data and redirects to dashboard."""
    playlist_data = generate_dummy_data()
    playlist_id = 'demo-data'
    
    # Check if demo already exists in history to avoid duplicates or update it
    history = request.session.get('history', [])
    
    # Remove existing demo if present so we can add a fresh one at the end
    history = [p for p in history if p['id'] != playlist_id]
    
    playlist_obj = {
        'id': playlist_id,
        'name': 'Demo Playlist',
        'data': playlist_data,
        'created_at': datetime.now().isoformat()
    }
    
    history.append(playlist_obj)
    request.session['history'] = history
    request.session.modified = True # Ensure session is saved
    
    return redirect('dashboard', playlist_id=playlist_id)

def dashboard(request, playlist_id=None):
    history = request.session.get('history', [])
    
    if not history:
        return redirect('upload_file')
    
    selected_playlist = None
    if playlist_id:
        # Find requested playlist
        for p in history:
            if p['id'] == playlist_id:
                selected_playlist = p
                break
    
    # Default to most recent if not found or not provided
    if not selected_playlist:
        selected_playlist = history[-1]
        # If ID was provided but not found, redirect to valid URL
        if playlist_id: 
             return redirect('dashboard', playlist_id=selected_playlist['id'])

    context = build_dashboard_context(selected_playlist['data'], playlist_name_override=selected_playlist['name'])
    context['recommendations'] = build_recommendations(selected_playlist['data'])
    
    # Spotify Recommendations ("Deep Cuts")
    spotify = get_spotify_service(request)
    if spotify:
        context['spotify_recommendations'] = spotify.get_missing_top_tracks(selected_playlist['data'])
        context['spotify_connected'] = True
    else:
        context['spotify_recommendations'] = []
        context['spotify_connected'] = False
            
    context['current_playlist_id'] = selected_playlist['id']
    
    return render(request, 'musicinsights/dashboard.html', context)

def delete_history(request, playlist_id):
    history = request.session.get('history', [])
    # Filter out the playlist with the given ID
    new_history = [p for p in history if p['id'] != playlist_id]
    request.session['history'] = new_history
    return redirect('dashboard')
