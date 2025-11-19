from django.db import models

class ContactMessage(models.Model):
    INQUIRY_CHOICES = [
        ('general', 'General Question'),
        ('technical', 'Technical Support'),
        ('listing', 'Listing Assistance'),
        ('account', 'Account Help'),
        ('contact', 'Contact Issues'),
        ('feature', 'Feature Request'),
        ('other', 'Other'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(
        max_length=20,
        choices=INQUIRY_CHOICES,
        default='general'
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    attachment = models.FileField(
        upload_to='contact_attachments/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} ({self.full_name})"

