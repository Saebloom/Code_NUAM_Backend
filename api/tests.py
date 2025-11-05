from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Calificacion, Instrumento, Mercado, Estado
from django.core.exceptions import ValidationError
from datetime import date
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

class CalificacionModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user('u1', password='pass')
		self.inst = Instrumento.objects.create(nombre='Inst A', tipo='Tipo', moneda='CLP')
		self.merc = Mercado.objects.create(nombre='Merc A', pais='CL', tipo='Bursatil')
		self.estado = Estado.objects.create(nombre='Vigente')

	def test_fecha_pago_no_menor_que_emision(self):
		cal = Calificacion(
			monto_factor=100,
			fecha_emision=date(2025,1,10),
			fecha_pago=date(2025,1,9),  # inválido
			usuario=self.user,
			instrumento=self.inst,
			mercado=self.merc,
			estado=self.estado
		)
		with self.assertRaises(ValidationError):
			cal.full_clean()

	def test_soft_delete_sets_is_active_and_updated_by(self):
		cal = Calificacion.objects.create(
			monto_factor=50,
			fecha_emision=date(2025,1,1),
			fecha_pago=date(2025,1,2),
			usuario=self.user,
			instrumento=self.inst,
			mercado=self.merc,
			estado=self.estado,
			created_by=self.user, updated_by=self.user
		)
		cal.soft_delete(user=self.user)
		cal.refresh_from_db()
		self.assertFalse(cal.is_active)
		self.assertEqual(cal.updated_by, self.user)

class CalificacionAPIPermissionsTests(APITestCase):
	def get_token_for(self, user):
		r = RefreshToken.for_user(user)
		return str(r.access_token)

	def setUp(self):
		self.u1 = User.objects.create_user('u1', password='pass')
		self.u2 = User.objects.create_user('u2', password='pass')
		self.inst = Instrumento.objects.create(nombre='I', tipo='t', moneda='CLP')
		self.merc = Mercado.objects.create(nombre='M', pais='CL', tipo='t')
		self.estado = Estado.objects.create(nombre='V')
		self.cal = Calificacion.objects.create(
			monto_factor=1,
			fecha_emision=date(2025,1,1),
			fecha_pago=date(2025,1,2),
			usuario=self.u1,
			instrumento=self.inst, mercado=self.merc, estado=self.estado,
			created_by=self.u1, updated_by=self.u1
		)

	def test_user_cannot_edit_others_calificacion(self):
		token = self.get_token_for(self.u2)
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
		resp = self.client.patch(f'/api/calificaciones/{self.cal.id}/', data={'monto_factor': 999})
		self.assertIn(resp.status_code, (403, 404))

	def test_owner_can_edit_their_calificacion(self):
		token = self.get_token_for(self.u1)
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
		resp = self.client.patch(f'/api/calificaciones/{self.cal.id}/', data={'monto_factor': 2}, format='json')
		self.assertIn(resp.status_code, (200, 204))
