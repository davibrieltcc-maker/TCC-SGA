from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Funcionario
from .forms import FuncionarioForm
from core.decorators import admin_required


@login_required
@admin_required
def lista(request):
    funcionarios = Funcionario.objects.select_related('usuario').filter(data_demissao__isnull=True)
    return render(request, 'funcionarios/lista.html', {'funcionarios': funcionarios})

@login_required
@admin_required
def detalhe(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    return render(request, 'funcionarios/detalhe.html', {'funcionario': func})

@login_required
@admin_required
def novo(request):
    form = FuncionarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Funcionário cadastrado!')
        return redirect('funcionarios:lista')
    return render(request, 'funcionarios/form.html', {'form': form, 'titulo': 'Novo Funcionário'})

@login_required
@admin_required
def editar(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    form = FuncionarioForm(request.POST or None, instance=func)
    if form.is_valid():
        form.save()
        messages.success(request, 'Funcionário atualizado!')
        return redirect('funcionarios:lista')
    return render(request, 'funcionarios/form.html', {'form': form, 'titulo': 'Editar Funcionário'})

@login_required
@admin_required
def excluir(request, pk):
    from datetime import date
    func = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        func.data_demissao = date.today()
        func.save()
        messages.success(request, 'Funcionário desligado.')
        return redirect('funcionarios:lista')
    return render(request, 'funcionarios/confirmar_exclusao.html', {'funcionario': func})
