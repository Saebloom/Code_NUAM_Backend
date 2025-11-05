from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un superusuario no interactivo usando variables de entorno o argumentos.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for superuser')
        parser.add_argument('--email', type=str, help='Email for superuser')
        parser.add_argument('--password', type=str, help='Password for superuser')

    def handle(self, *args, **options):
        username = options.get('username') or os.environ.get('DJANGO_SUPERUSER_USERNAME') or 'admin'
        email = options.get('email') or os.environ.get('DJANGO_SUPERUSER_EMAIL') or 'admin@example.com'
        password = options.get('password') or os.environ.get('DJANGO_SUPERUSER_PASSWORD') or 'adminpass123'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Superusuario '{username}' ya existe. No se crea."))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado correctamente."))
