from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import pandas as pd
from .models import Delito, Estacion, Cuadrante, TIPO_DELITO_CHOICES
from django.db.models import Sum
from collections import defaultdict
from datetime import date 
from django.views.decorators.http import require_POST
from django.http import JsonResponse

def index(request):
    estaciones = Estacion.objects.all()
    return render(request, 'vigilancia/index.html', {
        'estaciones': estaciones,
    })

def cargar_excel(request):
    semanas_disponibles = Delito.objects.values_list('semana', flat=True).distinct().order_by('semana')
    estaciones_disponibles = Estacion.objects.filter(cuadrantes__delitos__isnull=False).distinct()

    if request.method == 'POST' and request.FILES.get('archivo'):
        excel_file = request.FILES['archivo']
        semana = request.POST.get('semana')

        if not semana or not semana.isdigit() or not (1 <= int(semana) <= 52):
            messages.error(request, "Número de semana inválido.")
            return render(request, 'vigilancia/cargar_excel.html', {
                'semanas': semanas_disponibles,
                'estaciones': estaciones_disponibles
            })

        semana = int(semana)

        # ✅ Mapeo actualizado según tu especificación
        MAPEO_TIPOS = {
            'Homicidio': 'homicidio',
            'Lesiones': 'lesiones',
            'Personas': 'hurto_personas',
            'Automotores': 'hurto_automotores',
            'Motocicletas': 'hurto_motocicletas',
            'Residencias': 'hurto_residencias',
            'Comercio': 'hurto_comercio',
        }

        TIPOS_VALIDOS = ', '.join(MAPEO_TIPOS.keys())

        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            messages.error(request, f"Error leyendo el archivo: {e}")
            return render(request, 'vigilancia/cargar_excel.html', {
                'semanas': semanas_disponibles,
                'estaciones': estaciones_disponibles
            })

        for _, row in df.iterrows():
            estacion_nombre = str(row['ESTACION']).strip()
            cuadrante_nombre = str(row['CUADRANTE']).strip()

            # Crear estación y cuadrante si no existen
            estacion, _ = Estacion.objects.get_or_create(nombre=estacion_nombre)
            cuadrante, _ = Cuadrante.objects.get_or_create(nombre=cuadrante_nombre, estacion=estacion)

            for col in df.columns:
                if col in ['ESTACION', 'CUADRANTE']:
                    continue

                try:
                    tipo_raw, anio = col.rsplit(' ', 1)
                    tipo_raw = tipo_raw.strip()
                    cantidad = row[col]

                    if pd.isna(cantidad) or int(cantidad) == 0:
                        continue

                    tipo_match = next((v for k, v in MAPEO_TIPOS.items() if k.lower() in tipo_raw.lower()), None)
                    if not tipo_match:
                        messages.warning(request, f"Tipo de delito no reconocido: '{tipo_raw}'. Debe coincidir con: {TIPOS_VALIDOS}")
                        continue

                    Delito.objects.create(
                        tipo=tipo_match,
                        fecha=date(int(anio), 7, 1),
                        cuadrante=cuadrante,
                        descripcion='Cargado desde Excel',
                        cantidad=int(cantidad),
                        semana=semana
                    )
                except Exception as e:
                    messages.error(request, f"Error procesando columna '{col}': {e}")

        messages.success(request, "Archivo procesado y delitos cargados correctamente.")
        return redirect('vigilancia:cargar_excel')

    return render(request, 'vigilancia/cargar_excel.html', {
        'semanas': semanas_disponibles,
        'estaciones': estaciones_disponibles
    })
    
def estacion(request, estacion_id):
    # Obtener la estación actual o lanzar 404 si no existe
    estacion = get_object_or_404(Estacion, id=estacion_id)

    # Obtener semana seleccionada desde query param (puede ser None)
    semana = request.GET.get('semana')

    # Filtrar delitos por estación (y semana si se especifica)
    delitos = Delito.objects.filter(cuadrante__estacion=estacion)
    if semana:
        delitos = delitos.filter(semana=semana)

    # Agrupar los datos por tipo y año usando defaultdict
    resumen = defaultdict(lambda: {'2023': 0, '2024': 0})
    for delito in delitos:
        año = delito.fecha.year
        if año in [2023, 2024]:
            tipo_normalizado = delito.tipo.strip().lower()
            resumen[tipo_normalizado][str(año)] += delito.cantidad

    # Preparar tabla para mostrar en la plantilla
    tabla = []
    for tipo_codigo, tipo_legible in TIPO_DELITO_CHOICES:
        tipo_normalizado = tipo_codigo.strip().lower()
        cantidad_2023 = resumen[tipo_normalizado]['2023']
        cantidad_2024 = resumen[tipo_normalizado]['2024']
        variacion = cantidad_2024 - cantidad_2023
        porcentaje = 0

        if cantidad_2023 > 0:
            porcentaje = (variacion / cantidad_2023) * 100
        elif cantidad_2024 > 0:
            porcentaje = 100

        tabla.append({
            'tipo': tipo_legible,
            '2023': cantidad_2023,
            '2024': cantidad_2024,
            'variacion': variacion,
            'porcentaje': porcentaje
        })

    # Obtener semanas disponibles en esa estación
    semanas_disponibles = (
        Delito.objects
        .filter(cuadrante__estacion=estacion)
        .values_list('semana', flat=True)
        .distinct()
        .order_by('semana')
    )

    return render(request, 'vigilancia/estacion.html', {
        'estacion': estacion,
        'tabla': tabla,
        'semanas': semanas_disponibles,
        'semana_seleccionada': semana,
    })


def cuadrante_dinamico(request):
    estaciones = Estacion.objects.all()
    return render(request, 'vigilancia/cuadrante_dinamico.html', {'estaciones': estaciones})

def cargar_cuadrantes(request):
    estacion_id = request.GET.get('estacion_id')
    cuadrantes = Cuadrante.objects.filter(estacion_id=estacion_id).values('id', 'nombre')
    return JsonResponse(list(cuadrantes), safe=False)

def cargar_datos_cuadrante(request):
    cuadrante_id = request.GET.get('cuadrante_id')
    semana = request.GET.get('semana')
    cuadrante = get_object_or_404(Cuadrante, id=cuadrante_id)

    delitos = Delito.objects.filter(cuadrante=cuadrante)
    if semana:
        delitos = delitos.filter(semana=int(semana))

    delitos_agrupados = (
        delitos
        .values('tipo', 'fecha__year')
        .annotate(total=Sum('cantidad'))
    )

    resumen = defaultdict(lambda: {2023: 0, 2024: 0})
    for d in delitos_agrupados:
        resumen[d['tipo']][d['fecha__year']] = d['total']

    tabla = []
    for tipo_cod, tipo_nombre in TIPO_DELITO_CHOICES:
        t23 = resumen[tipo_cod][2023]
        t24 = resumen[tipo_cod][2024]
        variacion = t24 - t23
        porcentaje = (variacion / t23 * 100) if t23 else (100 if t24 else 0)
        tabla.append({
            'tipo': tipo_nombre,
            '2023': t23,
            '2024': t24,
            'variacion': variacion,
            'porcentaje': round(porcentaje, 2),
        })

    return JsonResponse({'tabla': tabla})

def cargar_semanas_cuadrante(request):
    cuadrante_id = request.GET.get('cuadrante_id')

    semanas = (
        Delito.objects
        .filter(cuadrante_id=cuadrante_id)
        .exclude(semana__isnull=True)
        .values_list('semana', flat=True)
        .distinct()
        .order_by('semana')
    )

    return JsonResponse(list(semanas), safe=False)

def cargar_semanas_por_estacion(request):
    estacion_id = request.GET.get("estacion_id")
    semanas = (
        Delito.objects
        .filter(cuadrante__estacion_id=estacion_id)
        .exclude(semana__isnull=True)
        .values_list('semana', flat=True)
        .distinct()
        .order_by('semana')
    )
    return JsonResponse(list(semanas), safe=False)

def metropolitana(request):
    semana = request.GET.get('semana')  # opcional si usas filtro de semanas

    delitos = Delito.objects.all()

    # Filtrar por semana si aplica
    if semana:
        delitos = delitos.filter(semana=semana)

    tipos_delito = dict(Delito._meta.get_field('tipo').choices)

    # Tabla con sumas por tipo y año
    tabla = defaultdict(lambda: defaultdict(int))

    for delito in delitos:
        año = delito.fecha.year
        tipo = tipos_delito.get(delito.tipo, delito.tipo)
        tabla[tipo][año] += delito.cantidad  # ✅ aquí se corrige el error: sumar cantidad

    # Formatear tabla para mostrar en plantilla
    resultado = []
    for tipo, conteo in tabla.items():
        val_2023 = conteo.get(2023, 0)
        val_2024 = conteo.get(2024, 0)
        variacion = val_2024 - val_2023
        porcentaje = (variacion / val_2023 * 100) if val_2023 != 0 else (100.0 if val_2024 > 0 else 0.0)

        resultado.append({
            'tipo': tipo,
            2023: val_2023,
            2024: val_2024,
            'variacion': variacion,
            'porcentaje': porcentaje,
        })

    semanas = Delito.objects.values_list('semana', flat=True).distinct().order_by('semana')

    context = {
        'tabla': resultado,
        'semana_seleccionada': semana,
        'semanas': semanas,
    }
    return render(request, 'vigilancia/metropolitana.html', context)


@require_POST
def eliminar_semana(request):
    semana = request.POST.get('semana')

    if not semana or not semana.isdigit():
        messages.error(request, "Número de semana inválido.")
        return redirect('vigilancia:cargar_excel')

    semana = int(semana)
    delitos_a_eliminar = Delito.objects.filter(semana=semana)
    cantidad = delitos_a_eliminar.count()
    delitos_a_eliminar.delete()

    messages.success(request, f"Se eliminaron {cantidad} delitos registrados en la semana {semana}.")
    return redirect('vigilancia:cargar_excel')

def lista_estaciones(request):
    estaciones = Estacion.objects.all()
    return render(request, 'vigilancia/lista_estaciones.html', {'estaciones': estaciones})
