"""
ASGI config for nuam project.
"""

import os

from django.core.asgi import get_asgi_application

# CORREGIDO:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam.settings')

application = get_asgi_application()