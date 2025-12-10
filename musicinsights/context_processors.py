def recent_uploads(request):
    # Fetch history from session
    history = request.session.get('history', [])
    
    # Reverse to show newest first
    dashboard_list = list(reversed(history))
        
    return {'recent_uploads': dashboard_list}

def google_analytics(request):
    from django.conf import settings
    return {'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID}
