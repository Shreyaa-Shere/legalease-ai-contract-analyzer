"""
URL configuration for legalease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def root_view(request):
    """
    Root URL view - can redirect to React app or show API info.
    For now, returns simple message indicating this is the API backend.
    """
    return HttpResponse("""
        <h1>LegalEase API Backend</h1>
        <p>This is the Django REST API backend for LegalEase.</p>
        <p>API endpoints are available at:</p>
        <ul>
            <li><a href="/api/contracts/">/api/contracts/</a> - Contract endpoints</li>
            <li><a href="/api/token/">/api/token/</a> - JWT Authentication</li>
            <li><a href="/admin/">/admin/</a> - Django Admin Panel</li>
        </ul>
        <p>Frontend React app should be running separately (typically on port 3000).</p>
    """, content_type="text/html")

urlpatterns = [
    # Root URL - API info page
    path('', root_view, name='home'),
    
    # Admin panel - Django's built-in admin interface
    path('admin/', admin.site.urls),
    
    # REST API endpoints
    # All API URLs start with /api/
    path('api/', include('contracts.api_urls')),
]

# Serve media files during development
# This allows uploaded files (PDFs, DOCX) to be accessed via URL
# In production, you'd use a web server (nginx) or cloud storage instead
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
