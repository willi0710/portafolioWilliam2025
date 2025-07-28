from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def index(sequence, position):
    return sequence[position]

@register.filter
def stringformat(value, format_string):
    try:
        return ("%" + format_string) % value
    except Exception:
        return value

@register.filter
def range_to(start, end):
    try:
        return range(start, int(end))
    except Exception:
        return []

@register.filter
def minus(value, arg):
    try:
        return int(value) - int(arg)
    except Exception:
        return 0

@register.simple_tag
def combine_years(year1, year2):
    return f"{year1}-{year2}"

@register.filter
def nested_get(d, key):
    keys = key.split(',')
    for k in keys:
        d = d.get(int(k) if k.isdigit() else k, {})
    return d if d != {} else 0
