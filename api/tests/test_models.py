from django.test import TestCase
from django.contrib.auth.models import User
from api.models import CalificacionTributaria, Calificacion, Instrumento, Mercado, Estado
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal

class CalificacionTributariaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test_user', password='test_pass')
        self.inst = Instrumento.objects.create(nombre='Inst Test', tipo='Tipo', moneda='CLP')
        self.merc = Mercado.objects.create(nombre='Merc Test', pais='CL', tipo='Bursatil')
        self.estado = Estado.objects.create(nombre='Activo')
        self.calificacion = Calificacion.objects.create(
            monto_factor=100,
            fecha_emision=date(2025,1,1),
            fecha_pago=date(2025,1,2),
            usuario=self.user,
            instrumento=self.inst,
            mercado=self.merc,
            estado=self.estado
        )

    def test_valor_historico_no_mayor_que_evento_capital(self):
        trib = CalificacionTributaria(
            calificacion=self.calificacion,
            secuencia_evento=1,
            evento_capital=Decimal('100.0000'),
            anio=2025,
            valor_historico=Decimal('150.0000')  # Inválido por ser mayor
        )
        with self.assertRaises(ValidationError):
            trib.full_clean()

    def test_crear_calificacion_tributaria_valida(self):
        trib = CalificacionTributaria.objects.create(
            calificacion=self.calificacion,
            secuencia_evento=1,
            evento_capital=Decimal('100.0000'),
            anio=2025,
            valor_historico=Decimal('50.0000')
        )
        self.assertEqual(trib.secuencia_evento, 1)
        self.assertEqual(trib.evento_capital, Decimal('100.0000'))
        self.assertEqual(trib.valor_historico, Decimal('50.0000'))

    def test_soft_delete_cascade(self):
        trib = CalificacionTributaria.objects.create(
            calificacion=self.calificacion,
            secuencia_evento=1,
            evento_capital=Decimal('100.0000'),
            anio=2025
        )
        
        # Soft delete de la calificación padre
        self.calificacion.soft_delete(self.user)
        
        # Verificar que la calificación tributaria sigue existiendo pero está inactiva
        trib.refresh_from_db()
        self.assertFalse(trib.is_active)
        self.assertEqual(trib.updated_by, self.user)