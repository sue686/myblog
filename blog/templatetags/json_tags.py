import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def jsonify(obj):
    """将Python对象转换为JSON字符串"""
    return mark_safe(json.dumps(obj))

@register.filter
def to_json(value):
    """将值转换为安全的JSON字符串"""
    return mark_safe(json.dumps(value)) 