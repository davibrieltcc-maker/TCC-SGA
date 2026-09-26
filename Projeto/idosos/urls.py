from django.urls import path
from . import views

app_name = 'idosos'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/excluir/', views.excluir, name='excluir'),
    path('<int:idoso_pk>/vincular-familiar/', views.vincular_familiar, name='vincular_familiar'),
    path('<int:idoso_pk>/desvincular-familiar/<int:vinculo_pk>/', views.desvincular_familiar, name='desvincular_familiar'),
]
