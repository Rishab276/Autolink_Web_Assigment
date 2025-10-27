# byhumaa
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

def review_page(request):
    """Display the review page"""
    return render(request, 'Reviews/review.html')

def report_page(request):
    """Display the report page"""
    return render(request, 'Reviews/report.html')

def submit_review(request):
    """Handle review form submission"""
    # For now, just show success message
    return HttpResponse("Review submitted successfully! (Forms will work after we fix models)")

def submit_report(request):
    """Handle report form submission"""
    # For now, just show success message  
    return HttpResponse("Report submitted successfully! (Forms will work after we fix models)")

def recommendations_view(request):
    return render(request, 'Reviews/recommendations.html')
