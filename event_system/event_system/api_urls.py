from django.urls import path, include

urlpatterns = [
    path('auth/', include('events.auth_urls')),
    path('', include('events.urls')),
]
