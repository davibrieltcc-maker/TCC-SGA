from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard'), name='home'),

    # Core: auth + dashboard + usuários
    path('', include('core.urls')),

    # Apps
    path('idosos/', include('idosos.urls')),
    path('medicamentos/', include('medicamentos.urls')),
    path('consultas/', include('consultas.urls')),
    path('fisioterapia/', include('fisioterapia.urls')),
    path('atividades/', include('atividades.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('relatorios/', include('relatorios.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
