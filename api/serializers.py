# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Estado, Instrumento, Mercado, Archivo,
    Calificacion, CalificacionTributaria, FactorTributario,
    Log, Auditoria, Respaldo
)

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

    def get_rol(self, obj):
        # Usa la lógica unificada
        return obtener_rol_usuario(obj)

# (Serializers de modelos: Rol, Estado, etc.)

class EstadoSerializer(serializers.ModelSerializer):
    class Meta: model = Estado; fields = "__all__"
class InstrumentoSerializer(serializers.ModelSerializer):
    class Meta: model = Instrumento; fields = "__all__"
class MercadoSerializer(serializers.ModelSerializer):
    class Meta: model = Mercado; fields = "__all__"
class ArchivoSerializer(serializers.ModelSerializer):
    class Meta: model = Archivo; fields = "__all__"
class FactorTributarioSerializer(serializers.ModelSerializer):
    class Meta: 
        model = FactorTributario
        fields = "__all__"
        read_only_fields = ['calificacion_tributaria']
class CalificacionTributariaSerializer(serializers.ModelSerializer):
    factores = FactorTributarioSerializer(many=True, required=False)
    class Meta: 
        model = CalificacionTributaria
        fields = "__all__"
        read_only_fields = ['calificacion']

# (Serializer de Calificación)
class CalificacionSerializer(serializers.ModelSerializer):
    tributarias = CalificacionTributariaSerializer(many=True, required=False)
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


    def create(self, validated_data):
        # 1. Saca los datos anidados del 'paquete'
        tributarias_data = validated_data.pop('tributarias', [])
        
        # 2. Crea la Calificacion (el objeto padre)
        # (La vista ya añade el 'usuario' y 'created_by')
        calificacion = super().create(validated_data)

        # 3. Recorre los datos de las tributarias
        for tributaria_data in tributarias_data:
            # Saca los datos de los factores (los nietos)
            factores_data = tributaria_data.pop('factores', [])
            
            # Crea el objeto Tributaria (el hijo)
            tributaria = CalificacionTributaria.objects.create(
                calificacion=calificacion, 
                **tributaria_data
            )
            
            # 4. Recorre los datos de los factores
            for factor_data in factores_data:
                # Crea el objeto Factor (el nieto)
                FactorTributario.objects.create(
                    calificacion_tributaria=tributaria, 
                    **factor_data
                )
        
        return calificacion

# --- Current User Serializer ---
class CurrentUserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "rol"]

    def get_rol(self, obj):
        # Usa la lógica unificada
        return obtener_rol_usuario(obj)




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
        model = Auditoria
        fields = "__all__"


class RespaldoSerializer(serializers.ModelSerializer):
    """
    Serializer para el nuevo modelo Respaldo.
    """
    # Muestra el username del usuario que lo registró
    usuario = serializers.StringRelatedField(read_only=True)
    
    # Campo para recibir el ID del usuario al crear
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='usuario', write_only=True
    )

    class Meta:
        model = Respaldo
        fields = [
            'id', 'fecha', 'usuario', 'archivo', 
            'estado', 'creado_en', 'usuario_id'
        ]
        # Hacemos 'usuario' y 'creado_en' de solo lectura en la respuest
        read_only_fields = ['usuario', 'creado_en']