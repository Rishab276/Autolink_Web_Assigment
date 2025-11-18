# main/forms.py
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    INQUIRY_TYPE_CHOICES = [
        ('', 'Select inquiry type'),
        ('general', 'General Question'),
        ('technical', 'Technical Support'),
        ('listing', 'Listing Assistance'),
        ('account', 'Account Help'),
        ('contact', 'Contact Issues'),
        ('feature', 'Feature Request'),
        ('other', 'Other'),
    ]
    
    inquiry_type = forms.ChoiceField(
        choices=INQUIRY_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Please select an inquiry type',
            'invalid_choice': 'Please select a valid inquiry type'
        }
    )
    
    class Meta:
        model = ContactMessage
        fields = [
            'full_name',
            'email',
            'phone',
            'inquiry_type',
            'subject',
            'message',
            'attachment',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'your@email.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+230 xxxx xxxx'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Brief subject of your message',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control', 
                'placeholder': 'How can we help you?',
                'required': True
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_inquiry_type(self):
        inquiry_type = self.cleaned_data.get('inquiry_type')
        if not inquiry_type or inquiry_type == '':
            raise forms.ValidationError("Please select an inquiry type")
        
        valid_choices = [choice[0] for choice in self.INQUIRY_TYPE_CHOICES if choice[0] != '']
        if inquiry_type not in valid_choices:
            raise forms.ValidationError("Please select a valid inquiry type")
        
        return inquiry_type
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required")
        return email
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name:
            raise forms.ValidationError("Full name is required")
        if len(full_name.strip()) < 2:
            raise forms.ValidationError("Please enter a valid full name")
        return full_name.strip()
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject:
            raise forms.ValidationError("Subject is required")
        if len(subject.strip()) < 5:
            raise forms.ValidationError("Subject must be at least 5 characters long")
        return subject.strip()
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message:
            raise forms.ValidationError("Message is required")
        if len(message.strip()) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long")
        return message.strip()
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone validation - remove spaces and check if it starts with +
            phone = phone.strip()
            if phone and not phone.startswith('+'):
                raise forms.ValidationError("Phone number should start with country code (e.g., +230)")
        return phone