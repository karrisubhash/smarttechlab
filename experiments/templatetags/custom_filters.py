from django import template
register = template.Library()

@register.filter
def index(sequence, position):
    """Safely get index from list."""
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return ""

@register.filter
def to(start, end):
    """Usage: {% for i in 1|to:7 %}"""
    return range(start, end)
