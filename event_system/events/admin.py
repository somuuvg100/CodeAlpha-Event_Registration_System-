from django.contrib import admin
from .models import Event, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'date_time', 'capacity', 'created_by', 'created_at']
    list_filter = ['date_time', 'created_at', 'created_by']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at']
    date_hierarchy = 'date_time'
    ordering = ['-date_time']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registered_at']
    list_filter = ['status', 'registered_at', 'event']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['registered_at']
    date_hierarchy = 'registered_at'
    ordering = ['-registered_at']
