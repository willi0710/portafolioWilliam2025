from django.urls import path
from . import views

app_name = 'miPortafolio'

urlpatterns = [
    path('', views.index, name='index'),
    path('explaboral/', views.explaboral, name='explaboral'),
    path('proyectos/', views.proyectos_redirect, name='proyectos'),
]

