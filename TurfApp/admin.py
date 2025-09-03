from django.contrib import admin
from .models import TurfVenue, Booking, TurfUser, Rating, Transaction
from django.contrib.auth.admin import UserAdmin

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'turf', 'player', 'date', 'start_time', 'status')
    list_filter = ('status', 'date', 'turf')
    search_fields = ('player__name', 'turf__name')
    list_editable = ('status',)
    ordering = ('-date', '-start_time')
    raw_id_fields = ('player', 'turf')

@admin.register(TurfVenue)
class TurfVenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'price_per_hour', 'sports_type')
    list_filter = ('location', 'sports_type', 'owner')
    search_fields = ('name', 'location', 'owner__name')
    ordering = ('name',)
    raw_id_fields = ('owner',)

class CustomTurfUserAdmin(UserAdmin):
    list_display = ('username', 'name', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('name', 'phone', 'role', 'profile_picture')}),
    )
    
    # --- NEW: ADDED CUSTOM ACTIONS ---
    actions = ['block_users', 'unblock_users']

    def block_users(self, request, queryset):
        """Action to block (deactivate) selected users."""
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} user(s) have been successfully blocked.")
    block_users.short_description = "Block selected users"

    def unblock_users(self, request, queryset):
        """Action to unblock (activate) selected users."""
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} user(s) have been successfully unblocked.")
    unblock_users.short_description = "Unblock selected users"

admin.site.register(TurfUser, CustomTurfUserAdmin)
admin.site.register(Rating)
admin.site.register(Transaction)

admin.site.site_header = "OnlyTurf Admin Dashboard"
admin.site.site_title = "OnlyTurf Admin"
admin.site.index_title = "Welcome to the OnlyTurf Management Portal"

