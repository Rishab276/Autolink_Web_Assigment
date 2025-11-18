
from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'inquiry_type', 'subject', 'created_at', 'is_resolved')
    list_filter = ('inquiry_type', 'is_resolved', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')

