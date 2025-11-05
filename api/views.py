from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from django.core.cache import cache
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)
from .serializers import (
    UserSerializer, RolSerializer, EstadoSerializer, InstrumentoSerializer,
    MercadoSerializer, ArchivoSerializer, CalificacionSerializer,
    CalificacionTributariaSerializer, FactorTributarioSerializer,
    Log as LogModel
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from rest_framework import serializers


# USERS
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

# Instrumento
class InstrumentoViewSet(viewsets.ModelViewSet):
    queryset = Instrumento.objects.all()
    serializer_class = InstrumentoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

# Mercado
class MercadoViewSet(viewsets.ModelViewSet):
    queryset = Mercado.objects.all()
    serializer_class = MercadoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

# Estado
class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

# Archivo
class ArchivoViewSet(viewsets.ModelViewSet):
    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

# Calificacion
class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.select_related("instrumento", "mercado", "usuario", "estado").all()
    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        obj = super().get_object()
        cache_key = f'calificacion_{obj.id}'
        cached_obj = cache.get(cache_key)
        if not cached_obj:
            cache.set(cache_key, obj, timeout=300)  # Cache por 5 minutos
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
            # si el usuario no setea usuario_id en el payload, lo asignamos desde request.user
            usuario = self.request.user
            # allow admin to set any usuario via usuario_id in serializer; otherwise force current user
            data = serializer.validated_data
            if not data.get("usuario"):
                instance = serializer.save(usuario=usuario)
            else:
                instance = serializer.save()

            # Invalidar caché
            cache_key = f'calificacion_{instance.id}'
            cache.delete(cache_key)
            cache.delete('calificaciones_list')

    def perform_update(self, serializer):
        instance = serializer.save()
        Log.objects.create(
            accion="Actualizar calificacion",
            detalle=f"Calificacion {instance.id} actualizada por {self.request.user}",
            usuario=self.request.user,
            calificacion=instance
        )

    def perform_destroy(self, instance):
        Log.objects.create(
            accion="Eliminar calificacion",
            detalle=f"Calificacion {instance.id} eliminada por {self.request.user}",
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

# CalificacionTributaria
class CalificacionTributariaViewSet(viewsets.ModelViewSet):
    queryset = CalificacionTributaria.objects.all()
    serializer_class = CalificacionTributariaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

# FactorTributario
class FactorTributarioViewSet(viewsets.ModelViewSet):
    queryset = FactorTributario.objects.all()
    serializer_class = FactorTributarioSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

# Log (solo lectura)
class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.select_related("usuario", "calificacion").all().order_by("-fecha")
    serializer_class = serializers.ModelSerializer  # we'll implement quick serializer inline

    class SimpleLogSerializer(serializers.ModelSerializer):
        class Meta:
            model = Log
            fields = "__all__"

    def get_serializer_class(self):
        return self.SimpleLogSerializer

# Auditoria
class AuditoriaViewSet(viewsets.ModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = serializers.ModelSerializer

    class SimpleAudSerializer(serializers.ModelSerializer):
        class Meta:
            model = Auditoria
            fields = "__all__"

    def get_serializer_class(self):
        return self.SimpleAudSerializer
