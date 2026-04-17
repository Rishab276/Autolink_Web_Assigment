from django.db import models
from django.contrib.auth.models import User
from Vehicles.models import Vehicle


class SavedVehicle(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_vehicles')
    vehicle  = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')

    def __str__(self):
        return f"{self.user.username} saved {self.vehicle}"


class UploadedVehicle(Vehicle):
    class Meta:
        proxy        = True
        verbose_name = "Uploaded Vehicle"
        verbose_name_plural = "Uploaded Vehicles"


class ProfilePicture(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile_picture_obj'
    )
    picture     = models.ImageField(upload_to='profile_pictures/')
    uploaded_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        try:
            old = ProfilePicture.objects.get(pk=self.pk)
            if old.picture != self.picture:
                old.picture.delete(save=False)
        except ProfilePicture.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile picture — {self.user.username}"