from django import template

register = template.Library()

@register.simple_tag
def get_entrega(entregas, estudiante_id, actividad_id):
    """
    Busca la entrega de un estudiante en una actividad específica.
    Uso en template:
        {% get_entrega entregas estudiante.Act_id actividad.Act_id as entrega %}
    """
    return entregas.filter(
        Est=estudiante_id,
        Act=actividad_id
    ).first()