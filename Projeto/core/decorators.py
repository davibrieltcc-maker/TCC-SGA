from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def perfil_required(*perfis):
    """Restringe acesso por perfil. Admin sempre passa."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_administrador:
                return view_func(request, *args, **kwargs)
            if request.user.perfil in perfis:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('dashboard')
        return _wrapped_view
    return decorator


def saude_required(view_func):
    """Profissionais de saúde + admin. Familiar NÃO acessa edição."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.pode_ver_saude:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Acesso restrito a profissionais de saúde.')
        return redirect('dashboard')
    return _wrapped_view


def admin_required(view_func):
    """Apenas administrador."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_administrador:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('dashboard')
    return _wrapped_view


def admin_ou_recepcionista_required(view_func):
    """Admin e Recepcionista podem criar/editar usuários e idosos."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.pode_cadastrar_usuarios:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Apenas Administrador ou Recepcionista podem realizar esta ação.')
        return redirect('dashboard')
    return _wrapped_view


def familiar_bloqueado(view_func):
    """Bloqueia familiar de acessar views de edição."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_familiar:
            messages.error(request, 'Familiares têm acesso apenas de visualização.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def primeiro_acesso_required(view_func):
    """Redireciona usuário de primeiro acesso para definir senha."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'primeiro_acesso', False):
            if request.resolver_match.url_name != 'definir_senha':
                return redirect('definir_senha')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
