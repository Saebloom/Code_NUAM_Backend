# api/views.py
import logging
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
# 🔽 1. IMPORTACIÓN CORREGIDA: Añadimos IsAuthenticated
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria, Usuario
)

from .serializers import (
    UserSerializer, EstadoSerializer, InstrumentoSerializer,
    MercadoSerializer, ArchivoSerializer, CalificacionSerializer,
    CalificacionTributariaSerializer, FactorTributarioSerializer,
    LogSerializer, AuditoriaSerializer, 
    CurrentUserSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

logger = logging.getLogger('api')

# =============================================================
# VISTAS DE AUTENTICACIÓN
# =============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_nuam(request):
    """
    Login corporativo personalizado.
    """
    username = request.data.get('username', '').lower().strip()
    password = request.data.get('password')

    if not username.endswith('@nuam.cl'):
        return Response(
            {"detail": "Solo se permiten correos corporativos @nuam.cl"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user = authenticate(username=username, password=password) 
    
    if user is not None:
        if not user.is_active:
            return Response(
                {"detail": "La cuenta de usuario está deshabilitada."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        # Devolvemos el usuario (lo necesita index.html)
        serializer = CurrentUserSerializer(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        })
    else:
        return Response(
            {"detail": "Credenciales inválidas."},
            status=status.HTTP_401_UNAUTHORIZED
        )

# =============================================================
# VISTAS DE USUARIOS (ADMIN)
# =============================================================

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Usuarios.
    """
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UserSerializer

    # 🔽 2. ESTA ES LA CORRECCIÓN CRÍTICA
    def get_permissions(self):
        """
        Asigna permisos basados en la acción (el 'endpoint' llamado).
        """
        if self.action == 'create':
            # 'create' es el registro público del index.html
            permission_classes = [AllowAny]
        elif self.action == 'me':
            # 'me' debe ser accesible para CUALQUIER usuario logueado
            permission_classes = [IsAuthenticated]
        else:
            # El resto (list, update, delete, admin_create) es solo para Admins
            permission_classes = [IsAdminUser] 
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Maneja el REGISTRO PÚBLICO desde index.html.
        """
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password')
        rol_name = request.data.get('rol', 'corredor') 

        if not email or not password:
            return Response({"detail": "Email y password son requeridos."}, status=status.HTTP_400_BAD_REQUEST)
        if not email.endswith('@nuam.cl'):
             return Response({"detail": "Solo se permiten correos @nuam.cl"}, status=status.HTTP_400_BAD_REQUEST)
        if Usuario.objects.filter(username=email).exists():
            return Response({"detail": "Este email ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = Usuario.objects.create_user(
                    username=email, email=email, password=password,
                    first_name=request.data.get('first_name', ''),
                    last_name=request.data.get('last_name', ''),
                    is_active=True 
                )
                group, created = Group.objects.get_or_create(name=rol_name.capitalize())
                user.groups.add(group)
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'], permission_classes=[IsAdminUser])
    def admin_create(self, request):
        """
        Crea un usuario desde el panel de admin (dashboard.html), asignando un rol.
        """
        email = request.data.get('email', '').lower().strip()
        rol_name = request.data.get('rol', 'corredor') 

        if not email or not request.data.get('password'):
            return Response({"detail": "Email y password son requeridos."}, status=status.HTTP_400_BAD_REQUEST)
        if Usuario.objects.filter(username=email).exists(): 
            return Response({"detail": "Un usuario con este email (username) ya existe."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = Usuario.objects.create_user( 
                    username=email, email=email,
                    password=request.data.get('password'),
                    first_name=request.data.get('first_name', ''),
                    last_name=request.data.get('last_name', ''),
                    genero=request.data.get('genero', ''),
                    telefono=request.data.get('telefono', ''),
                    direccion=request.data.get('direccion', ''),
                    rut_documento=request.data.get('rut_documento', ''),
                    pais=request.data.get('pais', ''),
                    is_active=True 
                )
                if rol_name == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                else:
                    group, created = Group.objects.get_or_create(name=rol_name.capitalize())
                    user.groups.add(group)
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 🔽 3. FUNCIÓN 'UPDATE' (EDITAR) CORREGIDA Y ÚNICA 🔽
    def update(self, request, *args, **kwargs):
        """
        Maneja la EDICIÓN (PATCH) de un usuario desde el dashboard.
        Añade lógica para actualizar el rol.
        """
        partial = kwargs.pop('partial', True) 
        instance = self.get_object()
        
        # --- Lógica de ROL añadida ---
        rol_name = request.data.get('rol')
        if rol_name:
            if rol_name == 'admin':
                instance.is_staff = True
                instance.is_superuser = True
                instance.groups.clear() 
            else:
                group, created = Group.objects.get_or_create(name=rol_name.capitalize())
                instance.groups.set([group]) 
                instance.is_staff = False
                instance.is_superuser = False
            instance.save()
        # --- Fin de la lógica de ROL ---

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def disable_user(self, request, pk=None):
        try:
            user = self.get_object()
            if user.is_superuser:
                return Response({"detail": "No se puede deshabilitar a un superusuario."}, status=status.HTTP_403_FORBIDDEN)
            user.is_active = False
            user.save()
            return Response({"status": "usuario deshabilitado"}, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def enable_user(self, request, pk=None):
        try:
            user = self.get_object()
            user.is_active = True
            user.save()
            return Response({"status": "usuario habilitado"}, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['DELETE'], permission_classes=[IsAdminUser])
    def delete_permanent(self, request, pk=None):
        try:
            user = self.get_object()
            if user.is_superuser:
                # 🔽 4. CORREGIDO (era 4F_FORBIDDEN)
                return Response({"detail": "No se puede eliminar a un superusuario."}, status=status.HTTP_403_FORBIDDEN)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['GET'], permission_classes=[IsAdminUser])
    def by_role(self, request):
        try:
            admins = Usuario.objects.filter(is_superuser=True)
            supervisors = Usuario.objects.filter(groups__name='Supervisor') 
            corredores = Usuario.objects.filter(groups__name='Corredor')
            
            return Response({
                "administradores": UserSerializer(admins, many=True).data,
                "supervisores": UserSerializer(supervisors, many=True).data,
                "corredores": UserSerializer(corredores, many=True).data,
            })
        except Exception as e:
            return Response({"detail": f"Error al obtener roles. Asegúrese de que los grupos 'Supervisor' y 'Corredor' existan. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['GET']) # Permiso se maneja en get_permissions
    def me(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "No autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)

# =============================================================
# VISTAS DE CALIFICACIONES (CORE)
# =============================================================

class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all().order_by('-created_at')
    serializer_class = CalificacionSerializer
    permission_classes = [IsOwnerOrAdmin] 

    def get_queryset(self):
            """
            Filtra las calificaciones.
            Admin y Supervisor ven todo.
            Corredor ve solo lo suyo.
            """
            user = self.request.user
            
            queryset = Calificacion.objects.select_related(
                'usuario', 'instrumento', 'mercado', 'estado'
            ).prefetch_related(
                'tributarias', 'tributarias__factores'
            ).filter(is_active=True).order_by('-created_at')

            # ✅ CAMBIO: Añadimos la comprobación del grupo "Supervisor"
            if user.is_staff or user.groups.filter(name="Supervisor").exists():
                return queryset # Devuelve todo
            else:
                # Los demás (Corredor) solo ven sus propias calificaciones
                return queryset.filter(usuario=user)

    def retrieve(self, request, *args, **kwargs):
        # ...
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user, created_by=self.request.user, updated_by=self.request.user)
        # ...
        logger.info(f"Usuario {self.request.user.username} creó Calificación ID: {serializer.instance.id}")

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        # ...
        logger.info(f"Usuario {self.request.user.username} actualizó Calificación ID: {serializer.instance.id}")

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
        # ...
        logger.info(f"Usuario {self.request.user.username} deshabilitó Calificación ID: {instance.id}")
        
    @action(detail=False, methods=['GET'], permission_classes=[IsOwnerOrAdmin])
    def mis_calificaciones(self, request):
        # ...
        mis_calificaciones = self.get_queryset().filter(usuario=request.user, is_active=True)
        # ...
        serializer = self.get_serializer(mis_calificaciones, many=True)
        return Response(serializer.data)

# =============================================================
# VISTAS DE MODELOS GENÉRICOS (ADMIN/SELECTS)
# =============================================================

class InstrumentoViewSet(viewsets.ModelViewSet):
    queryset = Instrumento.objects.all()
    serializer_class = InstrumentoSerializer
    permission_classes = [IsAdminOrReadOnly]

class MercadoViewSet(viewsets.ModelViewSet):
    queryset = Mercado.objects.all()
    serializer_class = MercadoSerializer
    permission_classes = [IsAdminOrReadOnly]

class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAdminOrReadOnly]

class ArchivoViewSet(viewsets.ModelViewSet):
    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = [IsAdminOrReadOnly]

class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    queryset = CalificacionTributaria.objects.all()
    serializer_class = CalificacionTributariaSerializer
    permission_classes = [IsOwnerOrAdmin] 

class FactorTributarioViewSet(viewsets.ModelViewSet):
    queryset = FactorTributario.objects.all()
    serializer_class = FactorTributarioSerializer
    permission_classes = [IsOwnerOrAdmin]

class LogViewSet(viewsets.ReadOnlyModelViewSet):
        # ... (código serializer y permission_classes) ...
        permission_classes = [IsAuthenticated]
        serializer_class = LogSerializer
        
        def get_queryset(self):
            """
            Filtra los logs.
            Admin y Supervisor ven todo.
            Corredor ve solo sus propias acciones.
            """
            user = self.request.user
            
            # ✅ CAMBIO: Añadimos la comprobación del grupo "Supervisor"
            if user.is_staff or user.groups.filter(name="Supervisor").exists():
                return Log.objects.all().order_by('-fecha')
            else:
                # Los demás (Corredor) solo ven sus propias acciones
                return Log.objects.filter(usuario=user).order_by('-fecha')
# (Hacemos lo mismo para Auditoria, por si acaso)
class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Muestra la Auditoria.
    Los Admins ven todo. Los demás usuarios solo ven lo suyo.
    """
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAuthenticated] # <-- CAMBIO DE PERMISO

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Auditoria.objects.all().order_by('-fecha')
        else:
            return Auditoria.objects.filter(usuario=user).order_by('-fecha')