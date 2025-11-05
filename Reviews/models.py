#byhumaa
from django.db import models
from django.utils import timezone

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    author_name = models.CharField(max_length=100)
    email = models.EmailField()
    created_date = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} by {self.author_name}"

class Report(models.Model):
    reporter_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    report_content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Report: {self.subject} by {self.reporter_name}"






