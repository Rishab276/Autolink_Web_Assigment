from django.contrib import admin
from django.utils.html import format_html
from .models import SavedVehicle, UploadedVehicle, ProfilePicture


@admin.register(SavedVehicle)
class SavedVehicleAdmin(admin.ModelAdmin):
    list_display    = ['user', 'vehicle', 'uploader_name', 'vehicle_price', 'vehicle_year', 'saved_at']
    list_filter     = ['user', 'saved_at', 'vehicle__uploader']
    search_fields   = ['user__username', 'vehicle__make', 'vehicle__model', 'vehicle__uploader__username']
    readonly_fields = ['saved_at']

    def uploader_name(self, obj):
        return obj.vehicle.uploader.username
    uploader_name.short_description = 'Uploader'

    def vehicle_price(self, obj):
        return f"Rs {obj.vehicle.price}"
    vehicle_price.short_description = 'Price'

    def vehicle_year(self, obj):
        return obj.vehicle.year
    vehicle_year.short_description = 'Year'

@admin.register(UploadedVehicle)
class UploadedVehicleAdmin(admin.ModelAdmin):
    list_display  = ['make', 'model', 'year', 'price', 'uploader', 'fuel_type', 'transmission', 'is_rental', 'is_sold', 'is_rented']
    list_filter   = ['uploader', 'is_rental', 'fuel_type', 'transmission', 'type_of_vehicle', 'is_sold', 'is_rented']
    search_fields = ['make', 'model', 'uploader__username', 'uploader__email']

@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display    = ['user', 'thumbnail', 'uploaded_at']
    search_fields   = ['user__username', 'user__email']
    readonly_fields = ['uploaded_at', 'thumbnail']

    def thumbnail(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;'
                'border-radius:50%;object-fit:cover;" />',
                obj.picture.url
            )
        return "No photo"
    thumbnail.short_description = 'Photo'