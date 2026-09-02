# D:\dev\maestra_webpage\eventos\models.py
from django.db import models
from django.utils.text import slugify
import calendar
from datetime import date, timedelta

from bandas.models import procesar_y_optimizar_a_webp

class Evento(models.Model):
    banda = models.ForeignKey('bandas.Banda', on_delete=models.CASCADE, related_name='eventos')
    hora = models.DateTimeField()
    precio_preventa = models.DecimalField(max_digits=8, decimal_places=0, help_text="Precio de Preventa")
    precio_puerta = models.DecimalField(max_digits=8, decimal_places=0, help_text="Precio el día del evento")
    descripcion = models.TextField(blank=True, null=True)
    
    # Producción avanzada:
    poster = models.ImageField(upload_to='eventos/posters/', blank=True, null=True, help_text="Afiche del evento (Ideal 1080x1080)")
    link_entrada = models.URLField(blank=True, null=True, help_text="Link de ticketera o enlace de WhatsApp para compra")
    asistencia = models.PositiveIntegerField(default=0, help_text="Asistencia esperada o acumulada")
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    
    # Campo confidencial para el productor
    notas_confidenciales = models.TextField(blank=True, null=True, help_text="Notas internas y acuerdos financieros con la banda")

    def save(self, *args, **kwargs):
        if not self.slug:
            fecha_str = self.hora.strftime('%d-%m-%Y')
            texto_base = f"{self.banda.nombre}-{fecha_str}"
            self.slug = slugify(texto_base)

        if self.poster and (
            not self.pk
            or Evento.objects.get(pk=self.pk).poster != self.poster
        ):
            self.poster = procesar_y_optimizar_a_webp(self.poster)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.banda.nombre} - {self.hora.strftime('%d/%m/%Y')}"


class CarteleraMensual(models.Model):

    MESES = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    mes = models.PositiveSmallIntegerField(
        choices=MESES,
        verbose_name="Mes"
    )

    anio = models.PositiveSmallIntegerField(
        verbose_name="Año"
    )

    imagen = models.ImageField(
        upload_to="eventos/carteleras/",
        help_text="Cartelera mensual (ideal 1080x1350 px)"
    )

    descripcion = models.TextField(
        blank=True,
        help_text="Texto opcional para la página de cartelera."
    )

    creada_en = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Cartelera mensual"
        verbose_name_plural = "Carteleras mensuales"
        ordering = ["-anio", "-mes"]
        constraints = [
            models.UniqueConstraint(
                fields=["mes", "anio"],
                name="cartelera_unica_mes_anio"
            )
        ]

    def __str__(self):
        return f"Cartelera {self.get_mes_display()} {self.anio}"

    @classmethod
    def vigente(cls):
        """
        Devuelve la cartelera vigente.

        La cartelera de un mes comienza el último viernes
        del mes anterior.
        """

        hoy = date.today()

        # Último viernes del mes actual
        ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]

        ultimo_viernes = date(hoy.year, hoy.month, ultimo_dia)

        while ultimo_viernes.weekday() != 4:
            ultimo_viernes -= timedelta(days=1)

        # ¿Ya comenzó la cartelera del mes siguiente?
        if hoy >= ultimo_viernes:

            if hoy.month == 12:
                mes = 1
                anio = hoy.year + 1
            else:
                mes = hoy.month + 1
                anio = hoy.year

        else:

            mes = hoy.month
            anio = hoy.year

        return cls.objects.filter(
            mes=mes,
            anio=anio
        ).first()

    @property
    def esta_activa(self):
        cartelera_vigente = CarteleraMensual.vigente()

        return (
            cartelera_vigente is not None
            and cartelera_vigente.pk == self.pk
        )


class FinDeSemana(models.Model):
    viernes = models.ImageField(
        upload_to="eventos/fin_de_semana/",
        blank=True,
        null=True,
        verbose_name="Viernes",
    )
    sabado = models.ImageField(
        upload_to="eventos/fin_de_semana/",
        blank=True,
        null=True,
        verbose_name="Sábado",
    )
    domingo = models.ImageField(
        upload_to="eventos/fin_de_semana/",
        blank=True,
        null=True,
        verbose_name="Domingo",
    )

    class Meta:
        verbose_name = "Fin de semana en Maestra Vida"
        verbose_name_plural = "Fin de semana en Maestra Vida"

    def save(self, *args, **kwargs):
        campos_imagen = ("viernes", "sabado", "domingo")
        imagenes_anteriores = (
            FinDeSemana.objects.get(pk=self.pk)
            if self.pk
            else None
        )

        for campo in campos_imagen:
            imagen = getattr(self, campo)
            imagen_anterior = (
                getattr(imagenes_anteriores, campo)
                if imagenes_anteriores
                else None
            )
            imagen_cambiada = imagen and (
                not self.pk
                or not imagen._committed
                or imagen_anterior.name != imagen.name
            )
            if imagen_cambiada:
                setattr(self, campo, procesar_y_optimizar_a_webp(imagen))

        super().save(*args, **kwargs)

    def __str__(self):
        return "Fin de semana en Maestra Vida"
