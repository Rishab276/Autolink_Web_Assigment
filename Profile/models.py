from django.db import models
from django.contrib.auth.models import User
from Vehicles.models import Vehicle

class SavedVehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')  # prevent duplicates

    def __str__(self):
        return f"{self.user.username} saved {self.vehicle}"
