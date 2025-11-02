from rest_framework import serializers
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

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
    usuario_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), source="usuario")

    class Meta:
        model = Calificacion
        fields = [
            "id", "monto_factor", "fecha_emision", "fecha_pago",
            "usuario", "usuario_id", "instrumento", "mercado",
            "archivo", "estado", "fecha_registro", "tributarias"
        ]
        read_only_fields = ["fecha_registro", "usuario"]

    def create(self, validated_data):
        # usuario ya fue seteado por usuario_id
        return super().create(validated_data)
