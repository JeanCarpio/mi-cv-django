import os
import io
import zipfile
import requests  
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

    # Nota: Si las imágenes del PDF no salen, necesitaremos una función link_callback aquí.
    # Por ahora probamos así ya que arreglaste el template.
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Tuvimos errores <pre>' + html + '</pre>')
    return response

def seleccionar_certificados(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    # Recuperamos las listas
    experiencias = ExperienciaLaboral.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')
    cursos = CursoRealizado.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')
    reconocimientos = Reconocimiento.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')

    if request.method == "POST":
        seleccionados = request.POST.getlist("certificados")
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            archivos_agregados = 0
            
            # Headers para parecer un navegador real
            headers_fake = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            for item in seleccionados:
                try:
                    tipo, id_obj = item.split('_') 
                    
                    objeto = None
                    if tipo == 'exp':
                        objeto = ExperienciaLaboral.objects.filter(pk=id_obj).first()
                    elif tipo == 'cur':
                        objeto = CursoRealizado.objects.filter(pk=id_obj).first()
                    elif tipo == 'rec':
                        objeto = Reconocimiento.objects.filter(pk=id_obj).first()
                    
                    if objeto and objeto.certificado:
                        file_url = objeto.certificado.url
                        
                        # --- LA CORRECCIÓN MAESTRA ---
                        # Si la URL no termina en extensión conocida, forzamos .pdf
                        if not file_url.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                            file_url += ".pdf"
                        
                        # Descargamos
                        response = requests.get(file_url, headers=headers_fake)
                        
                        if response.status_code == 200:
                            # Creamos un nombre limpio para el archivo dentro del ZIP
                            # Usamos el ID para asegurar que sea único
                            filename = f"certificado_{tipo}_{id_obj}.pdf"
                            
                            zip_file.writestr(filename, response.content)
                            archivos_agregados += 1
                        else:
                            print(f"Error descargando {file_url}: Status {response.status_code}")

                except Exception as e:
                    print(f"Error procesando item {item}: {e}")

        if archivos_agregados == 0:
             return HttpResponse("No se pudieron descargar los archivos. Intenta volver a subir los certificados en el admin.")

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="mis_certificados.zip"'
        return response

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