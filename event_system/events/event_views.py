from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction
from .models import Event, Registration
from .serializers import EventSerializer, EventCreateSerializer, RegistrationSerializer
from .permissions import IsEventCreatorOrStaff


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'location']
    filterset_fields = []

    def get_queryset(self):
        queryset = Event.objects.all()
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            queryset = queryset.filter(date_time__gte=timezone.now())
        return queryset


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


class EventRegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        event_id = kwargs.get('pk')
        user = request.user

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if event is in the past
        if event.date_time < timezone.now():
            return Response(
                {"detail": "Cannot register for past events."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use transaction to prevent race conditions
        try:
            with transaction.atomic():
                # Check for existing registration
                existing_registration = Registration.objects.filter(
                    user=user,
                    event=event
                ).first()

                if existing_registration:
                    if existing_registration.status == 'confirmed':
                        return Response(
                            {"detail": "You are already registered for this event."},
                            status=status.HTTP_409_CONFLICT
                        )
                    else:
                        # Re-register after cancellation
                        existing_registration.status = 'confirmed'
                        existing_registration.save()
                        serializer = self.get_serializer(existing_registration)
                        return Response(
                            {
                                "detail": "Registration reactivated successfully.",
                                "registration": serializer.data
                            },
                            status=status.HTTP_201_CREATED
                        )

                # Check if event is full
                confirmed_count = event.registrations.filter(status='confirmed').count()
                if confirmed_count >= event.capacity:
                    return Response(
                        {"detail": "This event is fully booked."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Create new registration
                registration = Registration.objects.create(
                    user=user,
                    event=event,
                    status='confirmed'
                )
                serializer = self.get_serializer(registration)
                return Response(
                    {
                        "detail": "Registration successful.",
                        "registration": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegistrationListView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the logged-in user's registrations
        return Registration.objects.filter(user=self.request.user).select_related('event')


class RegistrationCancelView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        registration_id = kwargs.get('pk')
        user = request.user

        try:
            registration = Registration.objects.get(id=registration_id)
            
            # Check if the registration belongs to the user
            if registration.user != user:
                return Response(
                    {"detail": "You can only cancel your own registrations."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Cancel the registration
            registration.status = 'cancelled'
            registration.save()
            
            serializer = self.get_serializer(registration)
            return Response(
                {
                    "detail": "Registration cancelled successfully.",
                    "registration": serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Registration.DoesNotExist:
            return Response(
                {"detail": "Registration not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the created_by field to the current user
        serializer.save(created_by=self.request.user)


class EventUpdateDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateSerializer
    permission_classes = [IsAuthenticated, IsEventCreatorOrStaff]


class EventRegistrationsListView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated, IsEventCreatorOrStaff]

    def get_queryset(self):
        event_id = self.kwargs.get('pk')
        # Get the event
        try:
            event = Event.objects.get(id=event_id)
            # Check permission
            if not (self.request.user.is_staff or event.created_by == self.request.user):
                raise PermissionDenied("You don't have permission to view this event's registrations.")
            # Return all registrations for this event
            return Registration.objects.filter(event=event).select_related('user', 'event')
        except Event.DoesNotExist:
            return Registration.objects.none()
