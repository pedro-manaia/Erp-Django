from django import template
from core.utils import has_module as _has_module

register = template.Library()

@register.filter(name="has_module")
def has_module(user, module):
    return _has_module(user, module)
