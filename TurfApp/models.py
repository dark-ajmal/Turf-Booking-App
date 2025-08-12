from django.db import models
from django.contrib.auth.models import AbstractUser

class Turf(AbstractUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=10, default='player', choices=[
        ('player', 'Player'),
        ('owner', 'Turf Owner')
    ])
    
    def __str__(self):
        return f"{self.name} ({self.role})"

    
class Other_Turf(models.Model):
    owner = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='owned_turfs')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    sports_type = models.CharField(max_length=50)
    price_per_hour = models.CharField(max_length=20)
    image = models.ImageField(upload_to='turf_images/', blank=True, null=True)
    no_of_players = models.IntegerField(default=0)
