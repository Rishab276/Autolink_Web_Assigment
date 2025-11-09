from django import template
# Custom template filter to mask email addresses
register = template.Library()

@register.filter
def mask_email(email):
    if not email or '@' not in email:
        return email
    username, domain = email.split('@')
    # Keep first part, mask last 4 characters before @
    if len(username) > 4:
        masked_username = username[:-4] + '****'
    else:
        masked_username = '****'  # If username is too short
    return f"{masked_username}@{domain}"