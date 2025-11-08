from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Review, Report

def review_page(request):
    """Display the review page"""
    return render(request, 'Reviews/review.html')

def report_page(request):
    """Display the report page"""
    return render(request, 'Reviews/report.html')

def submit_review(request):
    """Handle review form submission"""
    if request.method == 'POST':
        # SAVE REVIEW TO DATABASE
        review = Review.objects.create(
            title=request.POST.get('title'),
            review_text=request.POST.get('review_text'),
            rating=request.POST.get('rating'),
            author_name=request.POST.get('author_name'),
            email=request.POST.get('email')
        )
        messages.success(request, 'Review submitted successfully and saved to database!')
        return redirect('/reviews/')  # Use direct URL path
    
    return HttpResponse("Use POST method to submit review")

def submit_report(request):
    """Handle report form submission"""
    if request.method == 'POST':
        # SAVE REPORT TO DATABASE
        report = Report.objects.create(
            reporter_name=request.POST.get('reporter_name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            report_content=request.POST.get('report_content')
        )
        messages.success(request, 'Report submitted successfully and saved to database!')
        return redirect('/reviews/report/')  # Use direct URL path
    
    return HttpResponse("Use POST method to submit report")

def recommendations_view(request):
    return render(request, 'Reviews/recommendations.html')