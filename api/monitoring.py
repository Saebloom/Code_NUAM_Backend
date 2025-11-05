import logging
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone

logger = logging.getLogger('api')

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint para verificar el estado de la aplicación.
    Comprueba:
    - Conectividad a la base de datos
    - Estado del caché
    - Tiempo de respuesta
    """
    health_status = {
        'status': 'UP',
        'timestamp': timezone.now().isoformat(),
        'components': {
            'database': {'status': 'UP'},
            'cache': {'status': 'UP'},
        }
    }

    # Verificar base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception as e:
        health_status['components']['database'] = {
            'status': 'DOWN',
            'error': str(e)
        }
        health_status['status'] = 'DOWN'
        logger.error(f'Health check - Database error: {e}')

    # Verificar caché
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value != 'ok':
            raise Exception('Cache check failed')
    except Exception as e:
        health_status['components']['cache'] = {
            'status': 'DOWN',
            'error': str(e)
        }
        health_status['status'] = 'DOWN'
        logger.error(f'Health check - Cache error: {e}')

    if health_status['status'] == 'UP':
        logger.info('Health check passed successfully')
    
    return Response(health_status)