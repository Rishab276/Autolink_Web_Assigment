# byhumaa
from django import forms
from .models import Review, Report

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'review_text', 'rating', 'author_name', 'email']
        widgets = {
            'rating': forms.HiddenInput(),  # We'll handle this via JavaScript
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reporter_name', 'email', 'subject', 'report_content']

