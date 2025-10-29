from django import template

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