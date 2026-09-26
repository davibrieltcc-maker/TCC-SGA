from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/definir-senha/', views.definir_senha, name='definir_senha'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Gestão de usuários
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
    path('usuarios/novo/', views.usuario_novo, name='usuario_novo'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/excluir/', views.usuario_excluir, name='usuario_excluir'),
]
