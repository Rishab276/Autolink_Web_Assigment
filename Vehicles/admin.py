from django.contrib import admin
from .models import Vehicle, VehicleImage

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'is_rental', 'is_sold','is_rented')
    search_fields = ('make', 'model', 'year')
    list_filter = ('fuel_type', 'transmission', 'is_rental','is_sold','is_rented')
    inlines = [VehicleImageInline]
    
admin.site.register(VehicleImage)

