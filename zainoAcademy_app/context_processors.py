from .models import Usuario
from .views import get_usuario_from_session  

def usuario_context(request):
    usuario = None
    try:
        usuario = get_usuario_from_session(request)
    except:
        pass
    return {"usuario": usuario}
