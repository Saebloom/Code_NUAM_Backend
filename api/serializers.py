# api/serializers.py
from rest_framework import serializers
<<<<<<< HEAD
from django.contrib.auth import get_user_model
=======
# 🛠️ Importar el modelo Usuario que heredaste
>>>>>>> 2a97614c31f07e96d1f08494c1912fc371e88871
from .models import (
    Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
<<<<<<< HEAD
    Log, Auditoria
=======
    Log, Auditoria, Usuario 
>>>>>>> 2a97614c31f07e96d1f08494c1912fc371e88871
)

<<<<<<< HEAD
User = get_user_model()

# --- LÓGICA DE ROL UNIFICADA ---
def obtener_rol_usuario(obj):
    """
    Función centralizada para obtener el rol de un usuario.
    """
    if obj.is_superuser:
        return "admin"
    # Busca por el nombre de grupo con 'S' mayúscula
    if obj.groups.filter(name="Supervisor").exists():
        return "supervisor"
    if obj.groups.filter(name="Corredor").exists():
        return "corredor"
    
    return obj.groups.first().name.lower() if obj.groups.exists() else "desconocido"
# ---------------------------------

=======
# ---------------------------
# 👤 SERIALIZER DE USUARIO
# ---------------------------
>>>>>>> 2a97614c31f07e96d1f08494c1912fc371e88871
class UserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True) 

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "rol", "is_staff", "is_superuser", "is_active",
            "genero", "telefono", "direccion", "rut_documento", "pais"
        ]
<<<<<<< HEAD

    def get_rol(self, obj):
        # Usa la lógica unificada
        return obtener_rol_usuario(obj)

# (Serializers de modelos: Rol, Estado, etc.)
=======
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            # Solo permitimos que se escriba la contraseña via el ViewSet (no aquí)
            'password': {'write_only': True, 'required': False} 
        }

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_rol(self, obj):
        if obj.is_superuser:
            return "admin"
        return obj.groups.first().name if obj.groups.exists() else "desconocido"
    
    def update(self, instance, validated_data):
        """Permite actualizar los datos del usuario (usado por PATCH)"""
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)

        # Campos personalizados
        instance.genero = validated_data.get("genero", instance.genero)
        instance.telefono = validated_data.get("telefono", instance.telefono)
        instance.direccion = validated_data.get("direccion", instance.direccion)
        instance.rut_documento = validated_data.get("rut_documento", instance.rut_documento)
        instance.pais = validated_data.get("pais", instance.pais)

        instance.save()
        return instance


# ---------------------------
# 🙋‍♀️ SERIALIZER USUARIO ACTUAL (ME)
# ---------------------------
class CurrentUserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()
    
    # 🛠️ CORRECCIÓN: Se eliminó source='...' porque es redundante
    genero = serializers.CharField(read_only=True)
    telefono = serializers.CharField(read_only=True)
    direccion = serializers.CharField(read_only=True)
    rut_documento = serializers.CharField(read_only=True)
    pais = serializers.CharField(read_only=True)


    class Meta:
        model = Usuario
        fields = [
            "id", "username", "email", "first_name", "last_name", "rol", 
            "genero", "telefono", "direccion", "rut_documento", "pais"
        ] 

    def get_rol(self, obj):
        if obj.is_superuser:
            return "admin"
        elif obj.groups.filter(name="Supervisor").exists():
            return "supervisor"
        elif obj.groups.filter(name="Corredor").exists():
            return "corredor"
        return "desconocido"

# ---------------------------
# 📋 SERIALIZERS DE MODELOS GENERALES (RESTAURADOS)
# ---------------------------
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = "__all__"
>>>>>>> 2a97614c31f07e96d1f08494c1912fc371e88871

class EstadoSerializer(serializers.ModelSerializer):
    class Meta: model = Estado; fields = "__all__"
class InstrumentoSerializer(serializers.ModelSerializer):
    class Meta: model = Instrumento; fields = "__all__"
class MercadoSerializer(serializers.ModelSerializer):
    class Meta: model = Mercado; fields = "__all__"
class ArchivoSerializer(serializers.ModelSerializer):
    class Meta: model = Archivo; fields = "__all__"
class FactorTributarioSerializer(serializers.ModelSerializer):
    class Meta: model = FactorTributario; fields = "__all__"
class CalificacionTributariaSerializer(serializers.ModelSerializer):
    factores = FactorTributarioSerializer(many=True, read_only=True)
    class Meta: model = CalificacionTributaria; fields = "__all__"

# (Serializer de Calificación)
class CalificacionSerializer(serializers.ModelSerializer):
    tributarias = CalificacionTributariaSerializer(many=True, read_only=True)
    usuario = UserSerializer(read_only=True) 
    instrumento = InstrumentoSerializer(read_only=True)
    mercado = MercadoSerializer(read_only=True)
    estado = EstadoSerializer(read_only=True)
    instrumento_id = serializers.PrimaryKeyRelatedField(
        queryset=Instrumento.objects.all(), source='instrumento', write_only=True
    )
    mercado_id = serializers.PrimaryKeyRelatedField(
        queryset=Mercado.objects.all(), source='mercado', write_only=True
    )
    estado_id = serializers.PrimaryKeyRelatedField(
        queryset=Estado.objects.all(), source='estado', write_only=True
    )
    class Meta:
        model = Calificacion
        fields = [
            "id", "monto_factor", "fecha_emision", "fecha_pago",
            "usuario", "instrumento", "mercado", "estado",
            "instrumento_id", "mercado_id", "estado_id",
            "archivo", "created_at", "tributarias"
        ]
        read_only_fields = [
            "created_at", "instrumento", "mercado", "estado"
        ]

# --- Current User Serializer ---
class CurrentUserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "rol"]

    def get_rol(self, obj):
        # Usa la lógica unificada
        return obtener_rol_usuario(obj)

class InstrumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrumento
        fields = "__all__"

class MercadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mercado
        fields = "__all__"

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = "__all__"


class LogSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Log (solo lectura).
    """
    # Muestra el username en lugar del ID
    usuario = serializers.StringRelatedField() 
    
    class Meta:
        model = Log
        fields = "__all__"

class AuditoriaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Auditoria (solo lectura).
    """
    # Muestra el username en lugar del ID
    usuario = serializers.StringRelatedField()
    
    class Meta:
<<<<<<< HEAD
        model = Auditoria
        fields = "__all__"
=======
        model = CalificacionTributaria
        fields = "__all__"

class CalificacionSerializer(serializers.ModelSerializer):
    tributarias = CalificacionTributariaSerializer(many=True, read_only=True)
    # 🛠️ Usar el modelo Usuario correcto
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
>>>>>>> 2a97614c31f07e96d1f08494c1912fc371e88871
