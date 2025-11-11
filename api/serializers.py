# api/serializers.py

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
<<<<<<< HEAD
    
    # 🛠️ Campos de perfil añadidos para lectura y escritura
    genero = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    rut_documento = serializers.CharField(required=False, allow_blank=True)
    pais = serializers.CharField(required=False, allow_blank=True)

=======
>>>>>>> 13e77f5 (se agrego la funcionalidad de corredor y supervisor, ademas de arreglar incompatibilidades entre el backend y el frontend)

    class Meta:
        model = Usuario 
        fields = [
            "id", "username", "email", "first_name", "last_name",
<<<<<<< HEAD
            "genero", "telefono", "direccion", "rut_documento", "pais", # <--- CAMPOS PERSONALIZADOS
            "groups", "rol", "is_staff", "is_superuser", "is_active",
=======
            "groups", "rol", "is_staff", "is_superuser",
            "is_active"
>>>>>>> 13e77f5 (se agrego la funcionalidad de corredor y supervisor, ademas de arreglar incompatibilidades entre el backend y el frontend)
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

# ---------------------------
# ✅ SERIALIZADOR CORREGIDO
# ---------------------------
class CalificacionSerializer(serializers.ModelSerializer):
    tributarias = CalificacionTributariaSerializer(many=True, read_only=True)
<<<<<<< HEAD
    usuario = UserSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Usuario.objects.all(), source="usuario"
=======
    
    # --- CAMBIO 1 ---
    # Hacemos que los campos de solo lectura muestren el objeto completo
    # (Esto hace que la tabla del Mantenedor muestre nombres en lugar de IDs)
    usuario = UserSerializer(read_only=True) 
    instrumento = InstrumentoSerializer(read_only=True)
    mercado = MercadoSerializer(read_only=True)
    estado = EstadoSerializer(read_only=True)

    # --- CAMBIO 2 ---
    # Estos campos son para la ESCRITURA (POST/PUT).
    # Aceptan los IDs que envía el formulario.
    instrumento_id = serializers.PrimaryKeyRelatedField(
        queryset=Instrumento.objects.all(), source='instrumento', write_only=True
>>>>>>> 13e77f5 (se agrego la funcionalidad de corredor y supervisor, ademas de arreglar incompatibilidades entre el backend y el frontend)
    )
    mercado_id = serializers.PrimaryKeyRelatedField(
        queryset=Mercado.objects.all(), source='mercado', write_only=True
    )
    estado_id = serializers.PrimaryKeyRelatedField(
        queryset=Estado.objects.all(), source='estado', write_only=True
    )
    
    # El campo 'usuario_id' se elimina por completo.
    # La vista (views.py) se encargará de asignar el usuario
    # automáticamente desde el token (request.user).

    class Meta:
        model = Calificacion
        fields = [
            "id", "monto_factor", "fecha_emision", "fecha_pago",
            "usuario",      # Para GET (read_only)
            "instrumento",  # Para GET (read_only)
            "mercado",      # Para GET (read_only)
            "estado",       # Para GET (read_only)
            
            # --- CAMBIO 3 ---
            # Campos para POST (write_only)
            "instrumento_id", 
            "mercado_id",
            "estado_id",
            
            "archivo", "created_at", "tributarias"
        ]
        # --- CAMBIO 4 ---
        # 'usuario' se agrega a read_only_fields porque
        # NUNCA debe venir del formulario, siempre del token.
        read_only_fields = [
            "created_at", "usuario", "instrumento", "mercado", "estado"
        ]
<<<<<<< HEAD
        read_only_fields = ["created_at", "usuario"]
        
    def create(self, validated_data):
        return super().create(validated_data)
=======

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
>>>>>>> 13e77f5 (se agrego la funcionalidad de corredor y supervisor, ademas de arreglar incompatibilidades entre el backend y el frontend)
