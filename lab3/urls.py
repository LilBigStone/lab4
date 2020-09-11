from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.contrib.staticfiles.urls import static
import sys
from news.views import custom_handler404, custom_handler500
from . import settings
handler404 = custom_handler404
handler500 = custom_handler500
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainApp.urls')),
    path('news/', include('news.urls')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
