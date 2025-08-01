# vigilancia/urls.py
from django.urls import path
from . import views

app_name = 'vigilancia'

urlpatterns = [
    path('', views.index, name='index'),
    path('estaciones/', views.lista_estaciones, name='lista_estaciones'),
    path('estacion/<int:estacion_id>/', views.estacion, name='estacion'),
    path('cargar_excel/', views.cargar_excel, name='cargar_excel'),
    path('eliminar_semana/', views.eliminar_semana, name='eliminar_semana'),
    path('cuadrante-interactivo/', views.cuadrante_dinamico, name='cuadrante_dinamico'),
    path('ajax/cargar-cuadrantes/', views.cargar_cuadrantes, name='cargar_cuadrantes'),
    path('ajax/cargar-datos-cuadrante/', views.cargar_datos_cuadrante, name='cargar_datos_cuadrante'),
    path('ajax/cargar-semanas-cuadrante/', views.cargar_semanas_cuadrante, name='cargar_semanas_cuadrante'),
    path('ajax/cargar-semanas-estacion/', views.cargar_semanas_cuadrante, name='cargar_semanas_por_estacion'),
    path('metropolitana/', views.metropolitana, name='metropolitana'),


]
