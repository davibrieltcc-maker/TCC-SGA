from collections import defaultdict

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrar_turnos_para_periodos(apps, schema_editor):
    """Converte as antigas linhas (idoso, data, turno) em RotinaPeriodo,
    agrupadas sob uma única RotinaDiaria por (idoso, data)."""
    RotinaDiaria = apps.get_model('atividades', 'RotinaDiaria')
    RotinaPeriodo = apps.get_model('atividades', 'RotinaPeriodo')

    grupos = defaultdict(list)
    for r in RotinaDiaria.objects.all().order_by('id'):
        grupos[(r.idoso_id, r.data)].append(r)

    for (_, __), linhas in grupos.items():
        principal = linhas[0]
        for linha in linhas:
            RotinaPeriodo.objects.create(
                rotina=principal,
                periodo=linha.turno,
                responsavel_id=linha.responsavel_id,
                banho_realizado=linha.banho_realizado,
                higiene_oral=linha.higiene_oral,
                troca_roupa=linha.troca_roupa,
                curativo=linha.curativo,
                obs_higiene=linha.obs_higiene,
                refeicoes_realizadas=linha.refeicoes_realizadas,
                aceitacao_alimentar=linha.aceitacao_alimentar,
                obs_alimentacao=linha.obs_alimentacao,
            )

        obs_extra = ' | '.join(
            linha.observacoes_gerais for linha in linhas[1:] if linha.observacoes_gerais
        )
        if obs_extra:
            principal.observacoes_gerais = (
                f"{principal.observacoes_gerais} | {obs_extra}"
                if principal.observacoes_gerais else obs_extra
            )
            principal.save(update_fields=['observacoes_gerais'])

        for linha in linhas[1:]:
            linha.delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atividades', '0002_checklistatividade_itemchecklist_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RotinaPeriodo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(choices=[('manha', 'Manhã (06h–12h)'), ('tarde', 'Tarde (12h–18h)'), ('noite', 'Noite (18h–06h)')], max_length=6)),
                ('banho_realizado', models.BooleanField(default=False, verbose_name='Banho Realizado')),
                ('higiene_oral', models.BooleanField(default=False, verbose_name='Higiene Oral')),
                ('troca_roupa', models.BooleanField(default=False, verbose_name='Troca de Roupa')),
                ('curativo', models.BooleanField(default=False, verbose_name='Curativo Realizado')),
                ('obs_higiene', models.TextField(blank=True, verbose_name='Obs. Higienização')),
                ('refeicoes_realizadas', models.CharField(blank=True, max_length=200, verbose_name='Refeições Realizadas')),
                ('aceitacao_alimentar', models.CharField(blank=True, choices=[('total', 'Total'), ('parcial', 'Parcial'), ('recusou', 'Recusou')], max_length=10, verbose_name='Aceitação Alimentar')),
                ('obs_alimentacao', models.TextField(blank=True, verbose_name='Obs. Alimentação')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('responsavel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='periodos_registrados', to=settings.AUTH_USER_MODEL)),
                ('rotina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periodos', to='atividades.rotinadiaria')),
            ],
            options={
                'verbose_name': 'Período da Rotina',
                'verbose_name_plural': 'Períodos da Rotina',
                'ordering': ['rotina', 'periodo'],
            },
        ),
        migrations.RunPython(migrar_turnos_para_periodos, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='rotinadiaria',
            unique_together=set(),
        ),
        migrations.RemoveField(model_name='rotinadiaria', name='turno'),
        migrations.RemoveField(model_name='rotinadiaria', name='responsavel'),
        migrations.RemoveField(model_name='rotinadiaria', name='banho_realizado'),
        migrations.RemoveField(model_name='rotinadiaria', name='higiene_oral'),
        migrations.RemoveField(model_name='rotinadiaria', name='troca_roupa'),
        migrations.RemoveField(model_name='rotinadiaria', name='curativo'),
        migrations.RemoveField(model_name='rotinadiaria', name='obs_higiene'),
        migrations.RemoveField(model_name='rotinadiaria', name='refeicoes_realizadas'),
        migrations.RemoveField(model_name='rotinadiaria', name='aceitacao_alimentar'),
        migrations.RemoveField(model_name='rotinadiaria', name='obs_alimentacao'),
        migrations.AlterModelOptions(
            name='rotinadiaria',
            options={'ordering': ['-data'], 'verbose_name': 'Rotina Diária', 'verbose_name_plural': 'Rotinas Diárias'},
        ),
        migrations.AlterUniqueTogether(
            name='rotinadiaria',
            unique_together={('idoso', 'data')},
        ),
        migrations.AlterUniqueTogether(
            name='rotinaperiodo',
            unique_together={('rotina', 'periodo')},
        ),
    ]
