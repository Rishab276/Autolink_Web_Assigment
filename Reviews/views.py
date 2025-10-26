from django.shortcuts import render

def recommendations_view(request):
    return render(request, 'Reviews/recommendations.html')

def report_view(request):
    return render(request, 'Reviews/report.html')

def review_view(request):
    return render(request, 'Reviews/review.html')

