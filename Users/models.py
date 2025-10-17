from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_TYPES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('renter', 'Renter'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    driver_license = models.CharField(max_length=50, blank=True, null=True)  

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    )

    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    description = models.TextField()
    contact_number = models.CharField(max_length=15)
    images = models.ImageField(upload_to='vehicles/')

    def __str__(self):
        return f"{self.title} ({self.vehicle_type})"