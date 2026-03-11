from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Replace or add a query parameter in the current URL
    Usage: {% url_replace page=1 %}
    """
    request = context.get('request')
    if not request:
        return ''
    
    # Get current query parameters
    params = request.GET.copy()
    
    # Update with new parameters
    for key, value in kwargs.items():
        params[key] = str(value)
    
    # Return encoded string
    return params.urlencode()