from django.urls import path
from .views import health_check, protected_endpoint
from .event_views import (
    EventListView,
    EventDetailView,
    EventRegistrationView,
    EventCreateView,
    EventUpdateDeleteView,
    EventRegistrationsListView,
    RegistrationListView,
    RegistrationCancelView
)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('protected/', protected_endpoint, name='protected'),
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/create/', EventCreateView.as_view(), name='event-create'),
    path('events/<str:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<str:pk>/update/', EventUpdateDeleteView.as_view(), name='event-update'),
    path('events/<str:pk>/register/', EventRegistrationView.as_view(), name='event-register'),
    path('events/<str:pk>/registrations/', EventRegistrationsListView.as_view(), name='event-registrations'),
    path('registrations/', RegistrationListView.as_view(), name='registration-list'),
    path('registrations/<str:pk>/cancel/', RegistrationCancelView.as_view(), name='registration-cancel'),
]
