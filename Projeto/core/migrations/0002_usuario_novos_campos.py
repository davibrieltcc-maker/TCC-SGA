from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='data_nascimento',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Nascimento'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='especialidade',
            field=models.CharField(
                blank=True, max_length=100, verbose_name='Especialidade',
                help_text='Preencha para Médico ou Fisioterapeuta'
            ),
        ),
        migrations.AddField(
            model_name='usuario',
            name='data_admissao',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Admissão'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='primeiro_acesso',
            field=models.BooleanField(
                default=True, verbose_name='Primeiro Acesso',
                help_text='Usuário deve definir senha no primeiro login'
            ),
        ),
    ]
