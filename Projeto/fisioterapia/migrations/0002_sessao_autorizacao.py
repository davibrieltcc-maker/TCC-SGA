from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fisioterapia', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='sessaofisioterapia',
            name='autorizada',
            field=models.BooleanField(
                default=False, verbose_name='Autorizada pelo Médico',
                help_text='Sessão só pode ser executada após autorização médica.'
            ),
        ),
        migrations.AddField(
            model_name='sessaofisioterapia',
            name='autorizado_por',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='sessoes_autorizadas',
                limit_choices_to={'perfil': 'medico'},
                to=settings.AUTH_USER_MODEL,
                verbose_name='Autorizado por'
            ),
        ),
        migrations.AddField(
            model_name='sessaofisioterapia',
            name='data_autorizacao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data da Autorização'),
        ),
    ]
