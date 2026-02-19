"""
URL Configuration — v5.3
- /api/docs/            → Swagger UI (sabke liye open)
- /api/auth/login/      → Login (auth=None — publicly accessible)
- /api/auth/logout/     → Logout (auth=None)
- /api/auth/me/         → Current user (Session Auth required)
- /api/weather/*        → Weather endpoints (auth=None — publicly accessible)
- /api/*                → Sab farm endpoints (Session Auth required)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from farm.api import api

urlpatterns = [
    path('admin/', admin.site.urls),

    # Single API — /api/docs/ par Swagger UI milega
    # Login:   POST /api/auth/login/
    # Docs:    GET  /api/docs/
    path('api/', api.urls),

    # Frontend pages
    path('', include('farm.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
