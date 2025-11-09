from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User, Group # Importaciones cruciales
from django.db import transaction, IntegrityError
from django.core.cache import cache
from django.contrib.auth import authenticate

from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)
from .serializers import (
    UserSerializer, RolSerializer, EstadoSerializer, InstrumentoSerializer,
    MercadoSerializer, ArchivoSerializer, CalificacionSerializer,
    CalificacionTributariaSerializer, FactorTributarioSerializer,
    CurrentUserSerializer
)

from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


# --------------------------
# 🎯 LOGIN CORPORATIVO (solo @nuam.cl)
# --------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_nuam(request):
    """
    Login que solo permite usuarios con correos @nuam.cl.
    Busca al usuario por email y autentica con su username real.
    Retorna access y refresh token si las credenciales son válidas.
    """
    email_input = request.data.get('username') 
    password = request.data.get('password')

    if not email_input or not password:
        return Response(
            {'detail': 'Debe proporcionar un usuario y una contraseña.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if not email_input.lower().endswith('@nuam.cl'):
        return Response(
            {'detail': 'Solo se permiten correos corporativos @nuam.cl.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 3. BUSCAR Y AUTENTICAR POR EMAIL (La lógica corregida)
    user = None
    try:
        user_obj = User.objects.get(email__iexact=email_input)
        user = authenticate(username=user_obj.username, password=password)
        
    except User.DoesNotExist:
        pass 

    # 4. Generar Respuesta
    if user is not None:
        refresh = RefreshToken.for_user(user)
        user_serializer = CurrentUserSerializer(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data,
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'detail': 'Credenciales inválidas.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

# --------------------------
# 🔐 USUARIOS
# --------------------------
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    # CORRECCIÓN: Añadido order_by('id') para evitar el 'UnorderedObjectListWarning'
    queryset = User.objects.all().order_by('id') 
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Devuelve la información del usuario autenticado"""
    serializer = CurrentUserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def disable_user(request, pk):
    """Deshabilita un usuario (solo admin)"""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado'}, status=404)
    user.is_active = False
    user.save()
    return Response({'detail': 'Usuario deshabilitado'})

# --------------------------
# ➕ CREACIÓN DE USUARIOS (POR ADMIN)
# --------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_user(request):
    """
    Crea un nuevo usuario (Corredor, Supervisor, o Admin)
    Añadido por el Administrador desde el dashboard.
    """
    data = request.data
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    rol = data.get('rol') 

    if not email or not password or not rol:
        return Response(
            {'detail': 'Email, contraseña y rol son requeridos.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    username = email

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # 3. Asignar Rol (Grupo)
        if rol == 'admin':
            user.is_staff = True 
            user.is_superuser = True
            user.save()

        elif rol == 'supervisor':
            supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')
            user.groups.add(supervisor_group)

        elif rol == 'corredor':
            corredor_group, _ = Group.objects.get_or_create(name='Corredor')
            user.groups.add(corredor_group)

        serializer = CurrentUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response(
            {'detail': 'Un usuario con este email ya existe.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': f'Ocurrió un error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# --------------------------
# 📈 REPORTE DE ROLES (NUEVO)
# --------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_users_by_role(request):
    """
    Devuelve listas de usuarios agrupados por sus roles 
    para la pestaña "Roles" del dashboard de admin.
    """
    try:
        admins = User.objects.filter(is_superuser=True, is_active=True)
        
        supervisor_group = Group.objects.get(name='Supervisor')
        supervisores = supervisor_group.user_set.filter(is_active=True)
        
        corredor_group = Group.objects.get(name='Corredor')
        corredores = corredor_group.user_set.filter(is_active=True)
        
        data = {
            'administradores': UserSerializer(admins, many=True).data,
            'supervisores': UserSerializer(supervisores, many=True).data,
            'corredores': UserSerializer(corredores, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)
        
    except Group.DoesNotExist as e:
        return Response({'detail': f'Error de configuración: El grupo {e} no existe. (Ve a /admin para crearlo)'}, status=500)
    except Exception as e:
        return Response({'detail': str(e)}, status=500)


# --------------------------
# 📄 INSTRUMENTO
# --------------------------
class InstrumentoViewSet(viewsets.ModelViewSet):
    queryset = Instrumento.objects.all()
    serializer_class = InstrumentoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# --------------------------
# 💹 MERCADO
# --------------------------
class MercadoViewSet(viewsets.ModelViewSet):
    queryset = Mercado.objects.all()
    serializer_class = MercadoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# --------------------------
# 📦 ESTADO
# --------------------------
class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# --------------------------
# 📁 ARCHIVO
# --------------------------
class ArchivoViewSet(viewsets.ModelViewSet):
    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# --------------------------
# ⭐ CALIFICACIÓN
# --------------------------
class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.select_related(
        "instrumento", "mercado", "usuario", "estado"
    ).prefetch_related('tributarias').all()

    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        estado = self.request.query_params.get('estado')
        mercado = self.request.query_params.get('mercado')

        if fecha_desde:
            queryset = queryset.filter(fecha_emision__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_emision__lte=fecha_hasta)
        if estado:
            queryset = queryset.filter(estado_id=estado)
        if mercado:
            queryset = queryset.filter(mercado_id=mercado)
        return queryset

    def get_object(self):
        obj = super().get_object()
        cache_key = f'calificacion_{obj.id}'
        cached_obj = cache.get(cache_key)
        if not cached_obj:
            cache.set(cache_key, obj, timeout=300)
        return obj

    def list(self, request, *args, **kwargs):
        cache_key = 'calificaciones_list'
        cached_data = cache.get(cache_key)
        if cached_data is None:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = self.get_paginated_response(serializer.data).data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
            cache.set(cache_key, data, timeout=300)
            return Response(data)
        return Response(cached_data)

    def perform_create(self, serializer):
        with transaction.atomic():
            usuario = self.request.user
            data = serializer.validated_data
            if not data.get("usuario"):
                instance = serializer.save(usuario=usuario)
            else:
                instance = serializer.save()
            cache.delete(f'calificacion_{instance.id}')
            cache.delete('calificaciones_list')

    def perform_update(self, serializer):
        instance = serializer.save()
        Log.objects.create(
            accion="Actualizar calificación",
            detalle=f"Calificación {instance.id} actualizada por {self.request.user}",
            usuario=self.request.user,
            calificacion=instance
        )

    def perform_destroy(self, instance):
        Log.objects.create(
            accion="Eliminar calificación",
            detalle=f"Calificación {instance.id} eliminada por {self.request.user}",
            usuario=self.request.user,
            calificacion=instance
        )
        instance.delete()

    @action(detail=False, methods=["get"])
    def mis_calificaciones(self, request):
        qs = self.queryset.filter(usuario=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# --------------------------
# 💼 CALIFICACIÓN TRIBUTARIA
# --------------------------
class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    queryset = CalificacionTributaria.objects.all()
    serializer_class = CalificacionTributariaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# --------------------------
# 📊 FACTOR TRIBUTARIO
# --------------------------
class FactorTributarioViewSet(viewsets.ModelViewSet):
    queryset = FactorTributario.objects.all()
    serializer_class = FactorTributarioSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# --------------------------
# 📜 LOGS
# --------------------------
class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.select_related("usuario", "calificacion").all().order_by("-fecha")

    class SimpleLogSerializer(serializers.ModelSerializer):
        class Meta:
            model = Log
            fields = "__all__"

    def get_serializer_class(self):
        return self.SimpleLogSerializer


# --------------------------
# 🕵️‍♀️ AUDITORÍA
# --------------------------
class AuditoriaViewSet(viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()

    class SimpleAudSerializer(serializers.ModelSerializer):
        class Meta:
            model = Auditoria
            fields = "__all__"

    def get_serializer_class(self):
        return self.SimpleAudSerializer