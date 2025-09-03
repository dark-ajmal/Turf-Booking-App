from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter(name='is_cancellable')
def is_cancellable(booking):
    """
    Checks if a booking can be cancelled (more than 2 hours away).
    """
    if booking.status != 'Confirmed':
        return False
    
    booking_start_datetime = timezone.make_aware(
        datetime.combine(booking.date, booking.start_time)
    )
    return booking_start_datetime > (timezone.now() + timedelta(hours=2))

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Allows dictionary key lookups in Django templates.
    """
    return dictionary.get(key)

# --- FIX: ADD THIS NEW FILTER ---
@register.filter(name='divide')
def divide(value, arg):
    """
    Divides the value by the argument. Returns 0 if division by zero.
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter(name='subtract')
def subtract(value, arg):
    """
    Subtracts the arg from the value.
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value
    
@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies the value by the argument.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
    