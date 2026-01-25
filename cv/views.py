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

    # 1. Recuperamos las listas
    experiencias = ExperienciaLaboral.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')
    cursos = CursoRealizado.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')
    reconocimientos = Reconocimiento.objects.filter(perfil=perfil, certificado__isnull=False).exclude(certificado='')

    if request.method == "POST":
        seleccionados = request.POST.getlist("certificados")
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            archivos_agregados = 0
            
            # --- DISFRAZ DE NAVEGADOR ---
            # Esto evita que Cloudinary nos bloquee por ser un script
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
                        # 1. Obtenemos la URL base de Cloudinary
                        file_url = objeto.certificado.url
                        
                        # 2. CORRECCIÓN DE EXTENSIÓN (El truco para el error 401)
                        # Cloudinary a veces devuelve la URL sin .pdf. 
                        # Buscamos la extensión real en el nombre del archivo guardado en BD.
                        nombre_archivo = objeto.certificado.name  # Ej: certificados/curso.pdf
                        ext = os.path.splitext(nombre_archivo)[1] # Ej: .pdf
                        
                        # Si la URL no termina en la extensión correcta, se la pegamos
                        if ext and not file_url.lower().endswith(ext.lower()):
                            file_url += ext

                        # 3. Descargamos usando los headers falsos
                        response = requests.get(file_url, headers=headers_fake)
                        
                        if response.status_code == 200:
                            # Usamos el nombre limpio del archivo para el ZIP
                            filename = os.path.basename(nombre_archivo)
                            zip_file.writestr(filename, response.content)
                            archivos_agregados += 1
                        else:
                            print(f"Error descargando {file_url}: Status {response.status_code}")

                except Exception as e:
                    print(f"Error procesando item {item}: {e}")

        if archivos_agregados == 0:
             return HttpResponse("No se pudieron descargar los archivos. Verifica que los certificados existan.")

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