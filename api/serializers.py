from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)

# ---------------------------
# User Serializers
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "groups", "rol", "is_staff", "is_superuser"
        ]

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_rol(self, obj):
        # Retorna el primer grupo como rol principal, o None si no tiene
        return obj.groups.first().name if obj.groups.exists() else None

# ---------------------------
# Model Serializers
# ---------------------------
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = "__all__"

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = "__all__"

class InstrumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrumento
        fields = "__all__"

class MercadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mercado
        fields = "__all__"

class ArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = "__all__"

class FactorTributarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactorTributario
        fields = "__all__"

class CalificacionTributariaSerializer(serializers.ModelSerializer):
    factores = FactorTributarioSerializer(many=True, read_only=True)

    class Meta:
        model = CalificacionTributaria
        fields = "__all__"

class CalificacionSerializer(serializers.ModelSerializer):
    tributarias = CalificacionTributariaSerializer(many=True, read_only=True)
    usuario = UserSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all(), source="usuario"
    )

    class Meta:
        model = Calificacion
        fields = [
            "id", "monto_factor", "fecha_emision", "fecha_pago",
            "usuario", "usuario_id", "instrumento", "mercado",
            "archivo", "estado", "created_at", "tributarias"
        ]
        read_only_fields = ["created_at", "usuario"]

    def create(self, validated_data):
        return super().create(validated_data)

# ---------------------------
# Current User Serializer
# ---------------------------
class CurrentUserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "rol"]

    def get_rol(self, obj):
        if obj.is_superuser:
            return "admin"
        elif obj.groups.filter(name="Supervisor").exists():
            return "supervisor"
        elif obj.groups.filter(name="Corredor").exists():
            return "corredor"
        else:
            return "desconocido"
