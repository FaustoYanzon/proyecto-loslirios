from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """
    Obtiene un valor de un diccionario usando una clave.
    Uso: {{ mi_dict|dict_get:mi_clave }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key, 0)

@register.filter
def add_days(value, days):
    """
    Añade días a una fecha.
    Uso: {{ fecha|add_days:7 }}
    """
    try:
        if isinstance(value, str):
            # Si es string, intentar parsearlo como fecha
            value = datetime.strptime(value, '%Y-%m-%d').date()
        
        if hasattr(value, 'date'):
            # Si es datetime, obtener solo la fecha
            value = value.date()
        
        # Añadir los días
        return value + timedelta(days=int(days))
    except (ValueError, TypeError, AttributeError):
        return value