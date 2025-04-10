from django import template
import os

register = template.Library()

@register.filter
def filename_only(value):
    """
    Returns the base name of a file path (from a FileField).
    """
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    return value # Return original value if it's not a file field or has no name