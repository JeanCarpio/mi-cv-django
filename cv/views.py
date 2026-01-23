import os
import io
import zipfile
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings

from .models import (
    DatosPersonales,
    ExperienciaLaboral,
    CursoRealizado,
    Reconocimiento,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage
)

def get_contexto_perfil(perfil):
    """Función auxiliar para no repetir código entre home y pdf"""
    return {
        'perfil': perfil,
        'experiencias': ExperienciaLaboral.objects.filter(
            perfil=perfil, activarparaqueseveaenfront=True
        ),
        'cursos': CursoRealizado.objects.filter(
            perfil=perfil, activarparaqueseveaenfront=True
        ),
        'reconocimientos': Reconocimiento.objects.filter(
            perfil=perfil, activarparaqueseveaenfront=True
        ),
        'productos_academicos': ProductoAcademico.objects.filter(
            perfil=perfil, activarparaqueseveaenfront=True
        ),
        'productos_laborales': ProductoLaboral.objects.filter(
            perfil=perfil, activarparaqueseveaenfront=True
        ),
        'ventas': VentaGarage.objects.filter(
            perfil=perfil, activarparaqueseveaenfront=True
        ),
    }



def welcome(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    return render(request, 'cv/welcome.html', {'perfil': perfil})




def home(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    context = get_contexto_perfil(perfil)
    return render(request, 'cv/home.html', context)


def descargar_cv_pdf(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    context = get_contexto_perfil(perfil)

    template = get_template('cv/cv_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="CV_{perfil.nombres}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Tuvimos errores <pre>' + html + '</pre>')
    return response


def seleccionar_certificados(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    # 1. Recuperamos las listas POR SEPARADO
    experiencias = ExperienciaLaboral.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')
    cursos = CursoRealizado.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')
    reconocimientos = Reconocimiento.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')

    if request.method == "POST":
        seleccionados = request.POST.getlist("certificados")
        
        # Crear ZIP en memoria
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            archivos_agregados = 0
            
            for item in seleccionados:
                # El valor vendrá así: "exp_1", "cur_5", "rec_2"
                # Separamos el tipo del ID
                try:
                    tipo, id_obj = item.split('_') 
                    
                    objeto = None
                    # Buscamos en el modelo correcto según el prefijo
                    if tipo == 'exp':
                        objeto = ExperienciaLaboral.objects.filter(pk=id_obj).first()
                    elif tipo == 'cur':
                        objeto = CursoRealizado.objects.filter(pk=id_obj).first()
                    elif tipo == 'rec':
                        objeto = Reconocimiento.objects.filter(pk=id_obj).first()
                    
                    # Si existe el archivo, lo agregamos al ZIP
                    if objeto and objeto.certificado:
                        file_path = objeto.certificado.path
                        if os.path.exists(file_path):
                            # Usamos el nombre original del archivo
                            zip_file.write(file_path, os.path.basename(file_path))
                            archivos_agregados += 1
                except Exception as e:
                    print(f"Error procesando item {item}: {e}")

        if archivos_agregados == 0:
             return HttpResponse("No seleccionaste archivos o no se encontraron en el servidor.")

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="mis_certificados.zip"'
        return response

    # Enviamos las 3 listas separadas al HTML
    return render(request, "cv/seleccionar_certificados.html", {
        "experiencias": experiencias,
        "cursos": cursos,
        "reconocimientos": reconocimientos
    })

def venta_garage(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    productos = VentaGarage.objects.filter(
        perfil=perfil, 
        activarparaqueseveaenfront=True
    ).order_by('-fechapublicacion')
    
    return render(request, 'cv/venta_garage.html', {
        'perfil': perfil,
        'productos': productos
    })