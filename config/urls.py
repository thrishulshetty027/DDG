from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('secretadmin/', admin.site.urls),   # Changed from /admin/ for security
    path('', include('apps.dogs.urls')),
]
