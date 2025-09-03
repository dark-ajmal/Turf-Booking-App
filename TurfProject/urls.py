from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line directs all main traffic to your app's urls.py file
    path('', include('TurfApp.urls')),
]

# --- THIS IS THE CRUCIAL PART THAT MUST BE IN THIS FILE ---
# It tells Django how to serve your static files (like the background)
# and media files (like turf photos) when you are in development mode.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
