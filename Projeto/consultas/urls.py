from django.urls import path
from . import views

app_name = 'consultas'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/excluir/', views.excluir, name='excluir'),
    path('prontuario/<int:idoso_pk>/', views.prontuario, name='prontuario'),
]
