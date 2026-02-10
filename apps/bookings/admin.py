from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("resource", "user", "start_at", "end_at", "status", "created_at")
    search_fields = ("resource__name", "user__email")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
