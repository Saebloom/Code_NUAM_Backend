from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.db import transaction, IntegrityError
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# 🛠️ Importar el modelo Usuario personalizado (tu AUTH_USER_MODEL)
from .models import (
    Usuario as User, 
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)
# 🛠️ Importación de Serializers (DEBE SER ESTA)
from .serializers import (
    UserSerializer, CurrentUserSerializer,
    RolSerializer, EstadoSerializer, InstrumentoSerializer, MercadoSerializer,
    ArchivoSerializer, CalificacionSerializer, CalificacionTributariaSerializer,
    FactorTributarioSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


# --------------------------
# 🎯 LOGIN CORPORATIVO
# --------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_nuam(request):
    """Login corporativo con validación de dominio @nuam.cl."""
    email_input = request.data.get('username') 
    password = request.data.get('password')

    if not email_input or not password:
        return Response({'detail': 'Debe proporcionar un usuario y una contraseña.'}, status=status.HTTP_400_BAD_REQUEST)
    if not email_input.lower().endswith('@nuam.cl'):
        return Response({'detail': 'Solo se permiten correos corporativos @nuam.cl.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = None
    try:
        user_obj = User.objects.get(email__iexact=email_input)
        user = authenticate(username=user_obj.username, password=password)
    except User.DoesNotExist:
        pass 

    if user is not None:
        refresh = RefreshToken.for_user(user)
        user_serializer = CurrentUserSerializer(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data,
        }, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)


# --------------------------
# 🔐 USUARIOS Y GESTIÓN (CRUD COMPLETO)
# --------------------------
class UserViewSet(viewsets.ModelViewSet): # 🛠️ ModelViewSet permite GET, POST, PUT, PATCH, DELETE
    queryset = User.objects.all().order_by('id') 
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # Solo admins pueden modificar o listar

    def partial_update(self, request, *args, **kwargs):
        """Permite actualizar parcialmente (PATCH) datos de usuario, rol y contraseña"""
        instance = self.get_object()
        data = request.data.copy()
        
        # 1. Manejar Contraseña
        new_password = data.pop('password', None)
        if new_password:
            instance.set_password(new_password)
            instance.save() 

        # 2. Manejar Rol (Grupos)
        if 'rol' in data:
            new_rol = data.pop('rol')
            instance.groups.clear() 
            instance.is_superuser = False
            instance.is_staff = False

            if new_rol == 'admin':
                instance.is_superuser = True
                instance.is_staff = True
            elif new_rol == 'supervisor':
                supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')
                instance.groups.add(supervisor_group)
                instance.is_staff = True
            elif new_rol == 'corredor':
                corredor_group, _ = Group.objects.get_or_create(name='Corredor')
                instance.groups.add(corredor_group)
            
            instance.save() # Guarda los cambios de is_superuser/is_staff/groups

        # 3. Serializer procesa el resto de los campos (first_name, last_name, genero, telefono, etc.)
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer) # Llama al update del Serializer
        
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Devuelve la información del usuario autenticado"""
    serializer = CurrentUserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


# 🛠️ POST 1: Deshabilitar Usuario (Soft Delete/Poner Inactivo)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def disable_user(request, pk):
    """Deshabilita un usuario (solo admin). Lo pone inactivo."""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado'}, status=404)
    # Protege al Superusuario actual de ser deshabilitado
    if user.is_superuser:
        return Response({'detail': 'No se puede deshabilitar al Superusuario principal.'}, status=status.HTTP_403_FORBIDDEN)
    
    user.is_active = False
    user.save()
    return Response({'detail': 'Usuario deshabilitado'}, status=200)

# 🛠️ POST 2: Habilitar Usuario (Reactivar)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def enable_user(request, pk):
    """Habilita (activa) un usuario (solo admin)."""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado'}, status=404)
    if user.is_active:
        return Response({'detail': 'El usuario ya está activo'}, status=status.HTTP_400_BAD_REQUEST)
    user.is_active = True
    user.save()
    return Response({'detail': 'Usuario habilitado con éxito'}, status=200)

# 🛠️ DELETE: Eliminar Usuario (Borrado Permanente)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user(request, pk):
    """Elimina permanentemente un usuario de la base de datos (solo admin)."""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado'}, status=404)
    if user.is_superuser:
        return Response({'detail': 'No se puede eliminar al Superusuario principal.'}, status=status.HTTP_403_FORBIDDEN)
    
    user.delete()
    return Response({'detail': 'Usuario eliminado permanentemente'}, status=204)

# --------------------------
# ➕ CREACIÓN DE USUARIOS (POR ADMIN)
# --------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_user(request):
    """Crea un nuevo usuario con rol asignado."""
    data = request.data
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    rol = data.get('rol') 
    
    # Campos personalizados
    genero = data.get('genero', '')
    telefono = data.get('telefono', '')
    direccion = data.get('direccion', '')


    if not email or not password or not rol:
        return Response(
            {'detail': 'Email, contraseña y rol son requeridos.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    username = email

    try:
        # 🛠️ Creación de usuario con campos personalizados
        # NOTA: Usamos .create() en el modelo personalizado.
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            genero=genero, 
            telefono=telefono,
            direccion=direccion
        )
        user.set_password(password) # Establecer la contraseña de forma segura
        
        if rol == 'admin':
            user.is_staff = True 
            user.is_superuser = True
        elif rol == 'supervisor':
            supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')
            user.groups.add(supervisor_group)
        elif rol == 'corredor':
            corredor_group, _ = Group.objects.get_or_create(name='Corredor')
            user.groups.add(corredor_group)

        user.save()
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
    """Devuelve listas de usuarios agrupados por sus roles."""
    try:
        admins = User.objects.filter(is_superuser=True, is_active=True)
        
        # 🛠️ CORRECCIÓN: Usar get_or_create para evitar el error si los grupos no existen
        supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')
        supervisores = supervisor_group.user_set.filter(is_active=True)
        
        corredor_group, _ = Group.objects.get_or_create(name='Corredor')
        corredores = corredor_group.user_set.filter(is_active=True)
        
        data = {
            'administradores': UserSerializer(admins, many=True).data,
            'supervisores': UserSerializer(supervisores, many=True).data,
            'corredores': UserSerializer(corredores, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'detail': f'Error al cargar roles. Asegúrate de haber ejecutado las migraciones y creado los grupos: {str(e)}'}, status=500)


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