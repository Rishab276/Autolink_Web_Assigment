#by humaa
from django.contrib import admin
from .models import Review, Report

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'rating', 'created_date', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_date']
    search_fields = ['title', 'author_name', 'review_text']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['subject', 'reporter_name', 'created_date', 'is_resolved']
    list_filter = ['is_resolved', 'created_date']
    search_fields = ['subject', 'reporter_name', 'report_content']

