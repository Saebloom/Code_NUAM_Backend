"""
WSGI config for nuam project.
"""

import os

from django.core.wsgi import get_wsgi_application

# CORREGIDO:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam.settings')

application = get_wsgi_application()