from django.urls import path
from . import views

app_name = 'medicamentos'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/excluir/', views.excluir, name='excluir'),
    path('prescricao/<int:idoso_pk>/nova/', views.nova_prescricao, name='nova_prescricao'),
    path('administracao/<int:prescricao_pk>/registrar/', views.registrar_administracao, name='registrar_administracao'),
]
