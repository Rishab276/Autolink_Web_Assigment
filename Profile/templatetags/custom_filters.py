from django import template
import math

register = template.Library()

@register.filter
def mask_email(email):
    if not email or '@' not in email:
        return email

    username, domain = email.split('@')
    length = len(username)

    # Show at least 1 character, roughly 40% of the username
    visible_chars = max(1, math.ceil(length * 0.4))

    # Mask the remaining characters
    masked_username = username[:visible_chars] + '*' * (length - visible_chars)

    return f"{masked_username}@{domain}"
