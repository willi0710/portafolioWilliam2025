# Generated by Django 5.2.3 on 2025-06-26 23:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cuadrante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Estacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Delito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('homicidio', 'Homicidio'), ('lesiones', 'Lesiones personales'), ('hurto_personas', 'Hurto a Personas'), ('hurto_automotores', 'Hurto de Automotores'), ('hurto_motocicletas', 'Hurto de Motocicletas'), ('hurto_residencias', 'Hurto a Residencias'), ('hurto_comercio', 'Hurto a Comercio')], max_length=30)),
                ('fecha', models.DateField()),
                ('descripcion', models.TextField(blank=True)),
                ('semana', models.PositiveIntegerField(blank=True, null=True)),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('cuadrante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delitos', to='vigilancia.cuadrante')),
            ],
        ),
        migrations.AddField(
            model_name='cuadrante',
            name='estacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuadrantes', to='vigilancia.estacion'),
        ),
        migrations.AlterUniqueTogether(
            name='cuadrante',
            unique_together={('nombre', 'estacion')},
        ),
    ]
