# api/views.py
import logging
import pandas as pd
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import HttpResponse

# Importaciones del proyecto
from .models import (
    Calificacion, Instrumento, Mercado, Estado, 
    Log, Auditoria, Respaldo, CalificacionTributaria, FactorTributario
)
from .serializers import (
    UserSerializer, CalificacionSerializer, LogSerializer, 
    RespaldoSerializer, InstrumentoSerializer, MercadoSerializer, 
    EstadoSerializer
)
from .producers import kafka_producer  # <--- Implementación Kafka Productor (Nicolas)

User = get_user_model()
logger = logging.getLogger('api')

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API RESTful para gestión de usuarios.
    Incluye endpoints especiales para el Dashboard de Admin.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Seguridad: Cada usuario ve su propio perfil, Admin ve todo
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna el perfil del usuario logueado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Agrupa usuarios por rol para el dashboard."""
        data = {
            "administradores": UserSerializer(User.objects.filter(is_superuser=True), many=True).data,
            "supervisores": UserSerializer(User.objects.filter(groups__name='Supervisor'), many=True).data,
            "corredores": UserSerializer(User.objects.filter(groups__name='Corredor'), many=True).data
        }
        return Response(data)

    @action(detail=False, methods=['post'])
    def admin_create(self, request):
        """Creación de usuario con validaciones extra (RUT, País)."""
        data = request.data
        try:
            # Crear usuario base
            user = User.objects.create_user(
                username=data['email'], # Username es el email
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                rut_documento=data.get('rut_documento'),
                pais=data.get('pais'),
                genero=data.get('genero'),
                telefono=data.get('telefono'),
                direccion=data.get('direccion')
            )
            
            # Asignar Rol (Grupo)
            rol_nombre = data.get('rol', 'corredor').capitalize()
            from django.contrib.auth.models import Group
            grupo, _ = Group.objects.get_or_create(name=rol_nombre)
            user.groups.add(grupo)
            
            # Si es admin
            if data.get('rol') == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()

            # Log de auditoría
            Log.objects.create(
                accion="Crear Usuario", 
                detalle=f"Se creó el usuario {user.email} con rol {rol_nombre}",
                usuario=request.user
            )

            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def disable_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "Usuario deshabilitado"})

    @action(detail=True, methods=['post'])
    def enable_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "Usuario habilitado"})
    
    @action(detail=True, methods=['delete'])
    def delete_permanent(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CalificacionViewSet(viewsets.ModelViewSet):
    """
    Maneja el CRUD de Calificaciones.
    Implementa: Productores Kafka, Filtros, Carga Masiva.
    """
    serializer_class = CalificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Calificacion.objects.filter(is_active=True)
        
        # Filtros por query params (Arquitectura Django limpia)
        usuario_email = self.request.query_params.get('usuario_email')
        anio = self.request.query_params.get('anio')
        cal_id = self.request.query_params.get('id')

        if usuario_email:
            queryset = queryset.filter(usuario__email=usuario_email)
        if cal_id:
            queryset = queryset.filter(id=cal_id)
        if anio:
            queryset = queryset.filter(fecha_emision__year=anio)

        # Regla de Negocio: Corredor solo ve las suyas (a menos que sea Supervisor/Admin)
        es_supervisor = user.groups.filter(name='Supervisor').exists()
        if not (user.is_superuser or es_supervisor):
            queryset = queryset.filter(usuario=user)
            
        return queryset

    def perform_create(self, serializer):
        """
        Sobreescribimos el guardado para integrar Kafka (Productor).
        """
        instance = serializer.save(usuario=self.request.user, created_by=self.request.user)
        
        # --- KAFKA PRODUCER (Implementación Nicolas) ---
        kafka_data = {
            "evento": "NUEVA_CALIFICACION",
            "id": instance.id,
            "instrumento": instance.instrumento.nombre if instance.instrumento else "N/A",
            "monto": float(instance.monto_factor),
            "usuario": instance.usuario.email
        }
        kafka_producer.enviar_evento('topic-calificaciones', kafka_data)
        # -----------------------------------------------

    @action(detail=False, methods=['get'])
    def mis_calificaciones(self, request):
        qs = Calificacion.objects.filter(usuario=request.user, is_active=True).order_by('-created_at')
        
        # Filtros adicionales
        cid = request.query_params.get('id')
        anio = request.query_params.get('anio')
        if cid: qs = qs.filter(id=cid)
        if anio: qs = qs.filter(fecha_emision__year=anio)
            
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def importar_csv(self, request):
        """Carga masiva desde Excel/CSV con manejo de errores."""
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({"error": "No se envió archivo"}, status=400)

        try:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            creados = 0
            errores = []

            # Transacción atómica para integridad de datos (Arquitectura Django)
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Buscamos IDs foráneos
                        inst = Instrumento.objects.get(id=row.get('Instrumento_ID'))
                        merc = Mercado.objects.get(id=row.get('Mercado_ID'))
                        est = Estado.objects.get(id=row.get('Estado_ID'))
                        
                        Calificacion.objects.create(
                            monto_factor=row.get('Monto'),
                            fecha_emision=row.get('Fecha_Emision'),
                            fecha_pago=row.get('Fecha_Pago'),
                            instrumento=inst, mercado=merc, estado=est,
                            usuario=request.user, created_by=request.user, updated_by=request.user
                        )
                        creados += 1
                    except Exception as e:
                        errores.append(f"Fila {index+2}: {str(e)}")
            
            return Response({"creados": creados, "errores": errores})

        except Exception as e:
            return Response({"error": f"Error procesando archivo: {str(e)}"}, status=500)

    @action(detail=False, methods=['get'])
    def exportar_csv(self, request):
        """Genera reporte Excel."""
        qs = self.get_queryset()
        
        # Creamos data para pandas
        data = []
        for c in qs:
            data.append({
                "ID": c.id,
                "Instrumento": c.instrumento.nombre if c.instrumento else "",
                "Mercado": c.mercado.nombre if c.mercado else "",
                "Monto": c.monto_factor,
                "Fecha Emision": c.fecha_emision,
                "Usuario": c.usuario.email if c.usuario else ""
            })
        
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
        df.to_excel(response, index=False)
        return response

# --- ViewSets Simples ---
class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all().order_by('-fecha')
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Supervisores y Admin ven todo, Corredor solo lo suyo (Manejo de permisos)
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Supervisor').exists():
            return Log.objects.all().order_by('-fecha')
        return Log.objects.filter(usuario=user).order_by('-fecha')

class RespaldoViewSet(viewsets.ModelViewSet):
    queryset = Respaldo.objects.all().order_by('-fecha')
    serializer_class = RespaldoSerializer
    permission_classes = [permissions.IsAdminUser]

class InstrumentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Instrumento.objects.all()
    serializer_class = InstrumentoSerializer

class MercadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mercado.objects.all()
    serializer_class = MercadoSerializer

class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer