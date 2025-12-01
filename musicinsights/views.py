from django.shortcuts import render, redirect, get_object_or_404
from .models import Upload
from .services.exportify_parser import parse_exportify_file
from .services.stats_service import build_dashboard_context
from .services.recommendation_service import build_recommendations

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            upload = Upload.objects.create(original_file=request.FILES['file'])
            parse_exportify_file(upload)  
            return redirect('dashboard', upload_id=upload.id)
        except ValueError as e:
            return render(request, 'musicinsights/upload.html', {'error': str(e)})
    return render(request, 'musicinsights/upload.html')

def dashboard(request, upload_id):
    upload = get_object_or_404(Upload, id=upload_id)
    context = build_dashboard_context(upload)
    context['recommendations'] = build_recommendations(upload)
    return render(request, 'musicinsights/dashboard.html', context)
