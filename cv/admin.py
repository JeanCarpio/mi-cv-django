from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    DatosPersonales,
    ExperienciaLaboral,
    Reconocimiento,
    CursoRealizado,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage
)

@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # CORREGIDO: Antes era 'idperfil', ahora es 'id'
        'apellidos',
        'nombres',
        'numerocedula',
        'perfilactivo'
    )
    search_fields = ('apellidos', 'nombres', 'numerocedula')
    list_filter = ('perfilactivo', 'sexo')
    ordering = ('apellidos',)


@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = (
        'cargodesempenado',
        'nombrempresa',
        'fechainiciogestion',
        'fechafingestion',
        'activarparaqueseveaenfront'
    )
    list_filter = ('activarparaqueseveaenfront',)
    search_fields = ('cargodesempenado', 'nombrempresa')
    date_hierarchy = 'fechainiciogestion'


@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = (
        'descripcionreconocimiento',
        'tiporeconocimiento',
        'fechareconocimiento',
        'activarparaqueseveaenfront'
    )
    list_filter = ('tiporeconocimiento', 'activarparaqueseveaenfront')
    search_fields = ('descripcionreconocimiento', 'entidadpatrocinadora')
    date_hierarchy = 'fechareconocimiento'


@admin.register(CursoRealizado)
class CursoRealizadoAdmin(admin.ModelAdmin):
    list_display = (
        'nombrecurso',
        'fechainicio',
        'fechafin',
        'totalhoras',
        'activarparaqueseveaenfront'
    )
    list_filter = ('activarparaqueseveaenfront',)
    search_fields = ('nombrecurso', 'entidadpatrocinadora')
    date_hierarchy = 'fechainicio'


@admin.register(ProductoAcademico)
class ProductoAcademicoAdmin(admin.ModelAdmin):
    list_display = (
        'nombrerecurso',
        'clasificador',
        'activarparaqueseveaenfront'
    )
    list_filter = ('activarparaqueseveaenfront',)
    search_fields = ('nombrerecurso', 'clasificador')


@admin.register(ProductoLaboral)
class ProductoLaboralAdmin(admin.ModelAdmin):
    list_display = (
        'nombreproducto',
        'fechaproducto',
        'activarparaqueseveaenfront'
    )
    list_filter = ('activarparaqueseveaenfront',)
    search_fields = ('nombreproducto',)
    date_hierarchy = 'fechaproducto'


@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = (
        'nombreproducto',
        'estadoproducto',
        'valordelbien',
        'activarparaqueseveaenfront'
    )
    list_filter = ('estadoproducto', 'activarparaqueseveaenfront')
    search_fields = ('nombreproducto',)