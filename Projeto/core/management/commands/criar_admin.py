"""
Cria o administrador oficial do sistema.
Execute: python manage.py criar_admin
"""
from django.core.management.base import BaseCommand
from core.models import Usuario


class Command(BaseCommand):
    help = 'Cria o administrador oficial do sistema'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin')
        parser.add_argument('--password', required=True)
        parser.add_argument('--email', default='admin@asilo.com')
        parser.add_argument('--nome', default='Administrador')
        parser.add_argument('--sobrenome', default='Sistema')

    def handle(self, *args, **options):
        username = options['username']
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Usuário "{username}" já existe.'))
            return

        Usuario.objects.create_superuser(
            username=username,
            email=options['email'],
            password=options['password'],
            first_name=options['nome'],
            last_name=options['sobrenome'],
            perfil='administrador',
            primeiro_acesso=False,
            ativo=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Administrador "{username}" criado com sucesso!'
        ))
