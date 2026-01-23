from django.urls import path
from .views import home, descargar_cv_pdf, seleccionar_certificados, welcome, venta_garage

urlpatterns = [
    path('', welcome, name='welcome'), 
    path('hoja-de-vida/', home, name='home'), 
    path('cv/pdf/', descargar_cv_pdf, name='cv_pdf'),
    path('seleccionar_certificados/', seleccionar_certificados, name='seleccionar_certificados'),
    path('venta-garage/', venta_garage, name='venta_garage')
]