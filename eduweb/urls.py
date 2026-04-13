from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

handler404 = 'catalog.views.page_not_found'
handler500 = 'catalog.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),  # logout, password reset, etc.
    path('', include('catalog.urls')),
]

# Serve uploaded media files in development only.
# In production, your web server (nginx, etc.) should serve /media/ directly.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)