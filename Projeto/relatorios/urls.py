from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('familiar/', views.familiar_relatorio, name='familiar'),
    path('idosos/', views.idosos_relatorio, name='idosos'),
    path('medicamentos/', views.medicamentos_relatorio, name='medicamentos'),
    path('consultas/', views.consultas_relatorio, name='consultas'),
    path('fisioterapia/', views.fisioterapia_relatorio, name='fisioterapia'),
    path('atividades/', views.atividades_relatorio, name='atividades'),
]
