from django.urls import path
from . import views

app_name = 'atividades'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('checklist-do-dia/', views.atividades_do_dia, name='atividades_do_dia'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/excluir/', views.excluir, name='excluir'),

    path('<int:idoso_pk>/checklists/', views.checklist_lista, name='checklist_lista'),
    path('<int:idoso_pk>/checklists/novo/', views.checklist_novo, name='checklist_novo'),
    path('checklists/<int:pk>/editar/', views.checklist_editar, name='checklist_editar'),
    path('checklists/<int:pk>/encerrar/', views.checklist_encerrar, name='checklist_encerrar'),
]
