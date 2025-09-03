from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# User and Authentication Models
# -----------------------------------------------------------------------------

class TurfUser(AbstractUser):
    """
    The single, correct custom user model for both players and turf owners.
    """
    class Role(models.TextChoices):
        PLAYER = 'player', 'Player'
        OWNER = 'owner', 'Turf Owner'

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PLAYER)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Turf User"
        verbose_name_plural = "Turf Users"

    def __str__(self):
        return f"{self.name or self.username} ({self.get_role_display()})"

# -----------------------------------------------------------------------------
# Amenity Model
# -----------------------------------------------------------------------------

class Amenity(models.Model):
    """Represents a single, reusable amenity like 'Parking' or 'Floodlights'."""
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome class, e.g., 'fas fa-parking'")

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name

# -----------------------------------------------------------------------------
# Turf and Venue Models
# -----------------------------------------------------------------------------

class TurfVenue(models.Model):
    """
    Represents a specific turf venue that an owner can add and manage.
    """
    owner = models.ForeignKey(
        TurfUser, 
        on_delete=models.CASCADE, 
        related_name='owned_turfs',
        limit_choices_to={'role': TurfUser.Role.OWNER}
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    sports_type = models.CharField(max_length=50)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='turf_images/', blank=True, null=True)
    no_of_players = models.IntegerField(default=0)
    open_time = models.TimeField(blank=True, null=True)
    close_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    google_maps_link = models.URLField(max_length=500, blank=True, null=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    custom_amenities = models.CharField(max_length=255, blank=True, null=True, help_text="Enter comma-separated custom amenities.")
    
    class Meta:
        verbose_name = "Turf Venue"
        verbose_name_plural = "Turf Venues"
        ordering = ['name']

    def __str__(self):
        return self.name

# -----------------------------------------------------------------------------
# Booking and Reservation Models
# -----------------------------------------------------------------------------

class Booking(models.Model):
    turf = models.ForeignKey(TurfVenue, on_delete=models.CASCADE, related_name='bookings')
    player = models.ForeignKey(TurfUser, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    no_of_players = models.IntegerField(default=1, null=True, blank=True)

    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'), ('Blocked', 'Blocked'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    block_reason = models.CharField(max_length=100, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        if self.status == 'Blocked':
            return f"Blocked slot for {self.turf.name} on {self.date}"
        return f"Booking for {self.turf.name} by {self.player.name or 'N/A'} on {self.date}"

    @property
    def duration_in_hours(self):
        """Calculates the booking duration in hours. Returns float."""
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)
        return (end_datetime - start_datetime).total_seconds() / 3600

    @property
    def is_completed(self):
        """Returns True if the booking's end time is in the past."""
        if not self.date or not self.end_time:
            return False
        booking_end_datetime = timezone.make_aware(
            datetime.combine(self.date, self.end_time)
        )
        return booking_end_datetime < timezone.now()

class Rating(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='rating')
    player = models.ForeignKey(TurfUser, on_delete=models.CASCADE, related_name='ratings_given')
    turf = models.ForeignKey(TurfVenue, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rating for {self.turf.name} by {self.player.name}: {self.score} stars"
    
class Transaction(models.Model):
    """Represents a financial transaction for a booking."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('Completed', 'Completed'), ('Pending', 'Pending'), ('Failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction for Booking #{self.booking.id} - ₹{self.amount} ({self.status})"