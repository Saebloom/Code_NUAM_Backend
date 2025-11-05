from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Calificacion, Instrumento, Mercado, Estado, CalificacionTributaria
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date
from decimal import Decimal

class APIEndpointsTests(APITestCase):
    def setUp(self):
        # Crear usuarios
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin_pass')
        self.normal_user = User.objects.create_user('normal', 'normal@test.com', 'normal_pass')
        
        # Crear datos básicos
        self.inst = Instrumento.objects.create(nombre='Test Inst', tipo='Tipo', moneda='CLP')
        self.merc = Mercado.objects.create(nombre='Test Merc', pais='CL', tipo='Bursatil')
        self.estado = Estado.objects.create(nombre='Activo')

    def get_token_for(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_unauthorized_access(self):
        """Probar acceso sin autenticación"""
        response = self.client.get('/api/calificaciones/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_calificacion_with_tributarias(self):
        """Probar creación de calificación con calificaciones tributarias anidadas"""
        token = self.get_token_for(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {
            "monto_factor": "100.0000",
            "fecha_emision": "2025-01-01",
            "fecha_pago": "2025-01-02",
            "instrumento": self.inst.id,
            "mercado": self.merc.id,
            "estado": self.estado.id,
            "tributarias": [
                {
                    "secuencia_evento": 1,
                    "evento_capital": "50.0000",
                    "anio": 2025
                }
            ]
        }

        response = self.client.post('/api/calificaciones/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CalificacionTributaria.objects.count(), 1)

    def test_filter_calificaciones(self):
        """Probar filtrado de calificaciones"""
        token = self.get_token_for(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Crear algunas calificaciones
        Calificacion.objects.create(
            monto_factor=100,
            fecha_emision=date(2025,1,1),
            fecha_pago=date(2025,1,2),
            usuario=self.normal_user,
            instrumento=self.inst,
            mercado=self.merc,
            estado=self.estado
        )

        Calificacion.objects.create(
            monto_factor=200,
            fecha_emision=date(2025,2,1),
            fecha_pago=date(2025,2,2),
            usuario=self.normal_user,
            instrumento=self.inst,
            mercado=self.merc,
            estado=self.estado
        )

        # Probar filtro por fecha
        response = self.client.get('/api/calificaciones/', {
            'fecha_desde': '2025-01-15',
            'fecha_hasta': '2025-02-28'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_health_check(self):
        """Probar el endpoint de health check"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'UP')
        self.assertTrue('database' in response.data['components'])
        self.assertTrue('cache' in response.data['components'])