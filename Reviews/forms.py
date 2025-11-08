from django import forms
from .models import Review, Report

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'review_text', 'rating', 'author_name', 'email']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reporter_name', 'email', 'subject', 'report_content']