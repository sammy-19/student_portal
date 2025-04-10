from django import template
from django.utils.safestring import mark_safe
import re
import os

register = template.Library()

@register.filter
def youtube_embed_url(value):
    """
    Converts a YouTube watch URL into an embed URL.
    Handles various URL formats.
    """
    # Regular expression to match YouTube video IDs
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', value)
    if match:
        video_id = match.group(1)
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return mark_safe(embed_url)  # Mark as safe HTML
    return ''  # Return empty string if no match

@register.filter
def filename_only(value):
    """
    Returns the base name of a file path (from a FileField).
    """
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    return value # Return original value if it's not a file field or has no name