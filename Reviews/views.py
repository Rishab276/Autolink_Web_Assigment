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

from django.shortcuts import render
def submit_report(request):
    if request.method == 'POST':
        # Your existing code to save to database
        reporter_name = request.POST.get('reporter_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        report_content = request.POST.get('report_content')
        
        # Save to database
        Report.objects.create(
            reporter_name=reporter_name,
            email=email,
            subject=subject,
            report_content=report_content
        )
        
        # Render the same page with success message
        return render(request, 'Reviews/report.html', {'submitted': True})
    
    return render(request, 'Reviews/report.html')
    
    # If GET request, just render the page
    return render(request, 'report.html')
def recommendations_view(request):
    return render(request, 'Reviews/recommendations.html')