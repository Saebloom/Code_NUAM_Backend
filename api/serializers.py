from rest_framework import serializers
from .models import (
    Rol, Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria, Usuario # Importar tu modelo Usuario personalizado
)
from django.contrib.auth.models import Group # Importar Group para roles

# ---------------------------
# 👤 SERIALIZER DE USUARIO (Lectura/Escritura para CRUD)
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True) 
    
    # 🛠️ Campos de perfil añadidos para lectura y escritura
    genero = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    rut_documento = serializers.CharField(required=False, allow_blank=True)
    pais = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = Usuario 
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "genero", "telefono", "direccion", "rut_documento", "pais", # <--- CAMPOS PERSONALIZADOS
            "groups", "rol", "is_staff", "is_superuser", "is_active",
        ]
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'password': {'write_only': True, 'required': False} 
        }

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_rol(self, obj):
        if obj.is_superuser:
            return "admin"
        return obj.groups.first().name if obj.groups.exists() else "desconocido"


# ---------------------------
# 🙋‍♀️ SERIALIZER USUARIO ACTUAL (ME)
# ---------------------------
class CurrentUserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()
    # Incluir campos de perfil
    genero = serializers.CharField(read_only=True)
    telefono = serializers.CharField(read_only=True)
    direccion = serializers.CharField(read_only=True)
    rut_documento = serializers.CharField(read_only=True)
    pais = serializers.CharField(read_only=True)


    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "first_name", "last_name", "rol", "genero", "telefono", "direccion", "rut_documento", "pais"] 

    def get_rol(self, obj):
        if obj.is_superuser:
            return "admin"
        elif obj.groups.filter(name="Supervisor").exists():
            return "supervisor"
        elif obj.groups.filter(name="Corredor").exists():
            return "corredor"
        return "desconocido"


# ---------------------------
# 📋 SERIALIZERS DE MODELOS GENERALES (RESTAURADOS Y SINCRONIZADOS)
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
        write_only=True, queryset=Usuario.objects.all(), source="usuario"
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