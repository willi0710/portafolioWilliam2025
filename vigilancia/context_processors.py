from .models import Estacion

def estaciones_context(request):
    return {
        'estaciones': Estacion.objects.all()
    }
