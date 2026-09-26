from django.urls import path
from . import views

app_name = 'fisioterapia'

urlpatterns = [
    # Sessões
    path('', views.lista, name='lista'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('nova/', views.novo, name='novo'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/autorizar/', views.autorizar, name='autorizar'),
    path('<int:pk>/rejeitar/', views.rejeitar, name='rejeitar'),
    path('<int:pk>/evolucao/', views.registrar_evolucao, name='evolucao'),
    path('<int:pk>/excluir/', views.excluir, name='excluir'),
    # Planos de Reabilitação
    path('planos/', views.planos_lista, name='planos_lista'),
    path('planos/novo/', views.plano_novo, name='plano_novo'),
    path('planos/<int:pk>/editar/', views.plano_editar, name='plano_editar'),
    path('planos/<int:pk>/encerrar/', views.plano_excluir, name='plano_excluir'),
]
