import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from api.models import Calificacion, Instrumento, Mercado, Estado, Usuario

# Configura el logger para ver qué pasa en la consola
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Inicia el consumidor de Kafka para Calificaciones'

    def handle(self, *args, **options):
        # 1. Configuración del Consumidor
        conf = {
            'bootstrap.servers': 'localhost:9092', # Cambia esto si tu Kafka está en otro lado
            'group.id': 'grupo_valeska_backend',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        
        # 2. Suscribirse al "Topic" (el canal de noticias)
        topic = 'topic-calificaciones'
        consumer.subscribe([topic])
        
        self.stdout.write(self.style.SUCCESS(f'🎧 Escuchando mensajes en el topic: {topic} ...'))

        try:
            while True:
                # 3. Esperar mensajes (poll)
                msg = consumer.poll(1.0) # Espera 1 segundo

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Error de Kafka: {msg.error()}")
                        continue

                # 4. ¡Mensaje Recibido! Procesar datos
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    self.procesar_mensaje(data)
                except json.JSONDecodeError:
                    logger.error("El mensaje no es un JSON válido")
                except Exception as e:
                    logger.error(f"Error procesando mensaje: {e}")

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Deteniendo consumidor..."))
        finally:
            consumer.close()

    def procesar_mensaje(self, data):
        """
        Toma el diccionario (JSON) y lo convierte en una fila de base de datos.
        """
        try:
            # Buscamos las relaciones (Foreign Keys)
            # Asumimos que el mensaje trae el nombre del instrumento, mercado, etc.
            inst_obj, _ = Instrumento.objects.get_or_create(
                nombre=data.get('instrumento'),
                defaults={'tipo': 'Desconocido', 'moneda': 'USD'} # Valores por defecto si no existe
            )
            
            mercado_obj, _ = Mercado.objects.get_or_create(
                nombre=data.get('mercado'),
                defaults={'pais': 'CL', 'tipo': 'Bolsa'}
            )

            # Usamos el primer estado que exista o creamos uno
            estado_obj, _ = Estado.objects.get_or_create(nombre='Ingresado')
            
            # Asignamos un usuario por defecto (ej. el admin) para el registro
            usuario_admin = Usuario.objects.first() 

            # CREAR LA CALIFICACIÓN EN LA DB
            nueva_calif = Calificacion.objects.create(
                monto_factor=data.get('monto', 0),
                fecha_emision=data.get('fecha_emision'), # Formato esperado: YYYY-MM-DD
                fecha_pago=data.get('fecha_pago'),       # Formato esperado: YYYY-MM-DD
                instrumento=inst_obj,
                mercado=mercado_obj,
                estado=estado_obj,
                created_by=usuario_admin,
                usuario=usuario_admin
            )
            
            print(f"✅ Guardada Calificación ID {nueva_calif.id} - {inst_obj.nombre}")

        except Exception as e:
            print(f"❌ Error guardando en DB: {e}")