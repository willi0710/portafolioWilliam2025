from django.db import models
class Estacion(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()

    def __str__(self):
        return self.nombre

class Cuadrante(models.Model):
    nombre = models.CharField(max_length=50)
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, related_name='cuadrantes')

    class Meta:
        unique_together = ('nombre', 'estacion')  

    def __str__(self):
        return f"{self.nombre} - {self.estacion.nombre}"


TIPO_DELITO_CHOICES = [
    ('homicidio', 'Homicidio'),
    ('lesiones', 'Lesiones personales'),
    ('hurto_personas', 'Hurto a Personas'),
    ('hurto_automotores', 'Hurto de Automotores'),
    ('hurto_motocicletas', 'Hurto de Motocicletas'),
    ('hurto_residencias', 'Hurto a Residencias'),
    ('hurto_comercio', 'Hurto a Comercio'),
]

class Delito(models.Model):
    tipo = models.CharField(max_length=30, choices=TIPO_DELITO_CHOICES)
    fecha = models.DateField()  # Ej: 01-07-2023 para representar el año
    cuadrante = models.ForeignKey(Cuadrante, on_delete=models.CASCADE, related_name='delitos')
    descripcion = models.TextField(blank=True)
    semana = models.PositiveIntegerField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)  # 👈 NUEVO campo

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha.year} - {self.cantidad}"

