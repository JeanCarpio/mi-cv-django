from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from datetime import timedelta


class DatosPersonales(models.Model):
    descripcionperfil = models.CharField(max_length=50)
    perfilactivo = models.BooleanField(default=True)
    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20)
    lugarnacimiento = models.CharField(max_length=60)
    fechanacimiento = models.DateField()
    numerocedula = models.CharField(max_length=10, unique=True)

    sexo = models.CharField(
        max_length=1,
        choices=[('H', 'Hombre'), ('M', 'Mujer')]
    )

    fotoperfil = models.ImageField(
        upload_to='perfil/',
        blank=True,
        null=True
    )

    estadocivil = models.CharField(max_length=50)
    licenciaconducir = models.CharField(
        max_length=6,
        choices=[
            ('Tipo A', 'Tipo A'), ('Tipo B', 'Tipo B'), ('Tipo C', 'Tipo C'),
            ('Tipo D', 'Tipo D'), ('Tipo E', 'Tipo E'), ('Tipo F', 'Tipo F'),
            ('Tipo G', 'Tipo G')
        ]
    )
    telefonoconvencional = models.CharField(max_length=15)
    telefonofijo = models.CharField(max_length=15)
    direcciontrabajo = models.CharField(max_length=50)
    direcciondomiciliaria = models.CharField(max_length=50)
    sitioweb = models.URLField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

    def clean(self):
        if self.fechanacimiento > now().date():
            raise ValidationError(
                "La fecha de nacimiento no puede estar en el futuro"
            )


class ExperienciaLaboral(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    cargodesempenado = models.CharField(max_length=100)
    nombrempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50)
    emailempresa = models.EmailField(max_length=100)
    sitiowebempresa = models.URLField(max_length=100)
    nombrecontactoempresarial = models.CharField(max_length=100)
    telefonocontactoempresarial = models.CharField(max_length=60)
    fechainiciogestion = models.DateField()
    fechafingestion = models.DateField()
    descripcionfunciones = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    certificado = models.FileField(
        upload_to='certificados/experiencia/',
        blank=True,
        null=True
    )

    def clean(self):
        
        if self.fechafingestion < self.fechainiciogestion:
            raise ValidationError("La fecha fin no puede ser menor que la fecha inicio")

    
        if self.fechainiciogestion > now().date():
            raise ValidationError("La fecha de inicio no puede estar en el futuro")

        
        if self.fechafingestion > now().date():
            raise ValidationError("La fecha de fin no puede estar en el futuro (no puedes certificar experiencia que aún no ocurre).")


class Reconocimiento(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    tiporeconocimiento = models.CharField(
        max_length=100,
        choices=[
            ('Académico', 'Académico'),
            ('Público', 'Público'),
            ('Privado', 'Privado')
        ]
    )
    fechareconocimiento = models.DateField()
    descripcionreconocimiento = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100)
    telefonocontactoauspicia = models.CharField(max_length=15)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    certificado = models.FileField(
        upload_to='certificados/reconocimientos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.descripcionreconocimiento

    def clean(self):
        if self.fechareconocimiento > now().date():
            raise ValidationError("La fecha del reconocimiento no puede estar en el futuro")


class CursoRealizado(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    totalhoras = models.IntegerField(validators=[MinValueValidator(0)])
    descripcioncurso = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100)
    telefonocontactoauspicia = models.CharField(max_length=60)
    emailempresapatrocinadora = models.EmailField(max_length=60)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    certificado = models.FileField(
        upload_to='certificados/cursos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nombrecurso

    def clean(self):
        if self.fechafin < self.fechainicio:
            raise ValidationError("La fecha fin no puede ser menor que la fecha inicio")


class ProductoAcademico(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombrerecurso = models.CharField(max_length=100)
    clasificador = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    def __str__(self):
        return self.nombrerecurso


class ProductoLaboral(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=100)
    fechaproducto = models.DateField()
    descripcion = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreproducto

    def clean(self):
        if self.fechaproducto > now().date():
            raise ValidationError("La fecha del producto no puede estar en el futuro")



class VentaGarage(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=100)
    
    estadoproducto = models.CharField(
        max_length=40,
        choices=[
            ('Bueno', 'Bueno'),
            ('Regular', 'Regular')
        ]
    )

    descripcion = models.CharField(max_length=100)
    
    valordelbien = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    activarparaqueseveaenfront = models.BooleanField(default=True)
    
    fechapublicacion = models.DateField(default=now)
    imagen = models.ImageField(upload_to='venta_garage/', blank=True, null=True)

    def __str__(self):
        return self.nombreproducto

    def clean(self):
        # 1. Validar Futuro: No puedes publicar mañana
        if self.fechapublicacion > now().date():
            raise ValidationError("La fecha de publicación no puede estar en el futuro.")

        # 2. Validar Pasado Excesivo: 
        # Calculamos la fecha de hace 1 año exacto (365 días)
        fecha_limite_pasado = now().date() - timedelta(days=365)

        # Si la fecha que pusiste es MENOR (más vieja) que el límite... error.
        if self.fechapublicacion < fecha_limite_pasado:
            raise ValidationError("La fecha es demasiado antigua. No se permiten publicaciones de hace más de 1 año.")