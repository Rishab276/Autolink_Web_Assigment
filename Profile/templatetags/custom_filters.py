#MAIGHUN-2412258
from django import template
# Custom template filter to mask email addresses
register = template.Library()

@register.filter
def mask_email(email):
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@')
    
    # Always show only the first character
    first_char = username[0]
    
    # Mask everything else
    masked_username = first_char + '*' * (len(username) - 1)
    
    return f"{masked_username}@{domain}"
