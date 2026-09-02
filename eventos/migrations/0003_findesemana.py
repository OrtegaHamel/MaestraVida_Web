from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eventos', '0002_carteleramensual'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinDeSemana',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'viernes',
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='eventos/fin_de_semana/',
                        verbose_name='Viernes',
                    ),
                ),
                (
                    'sabado',
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='eventos/fin_de_semana/',
                        verbose_name='Sábado',
                    ),
                ),
                (
                    'domingo',
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to='eventos/fin_de_semana/',
                        verbose_name='Domingo',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Fin de semana en Maestra Vida',
                'verbose_name_plural': 'Fin de semana en Maestra Vida',
            },
        ),
    ]
