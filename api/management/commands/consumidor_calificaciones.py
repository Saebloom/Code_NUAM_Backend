import json
import logging
import sys
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaError
from api.models import Calificacion, Instrumento, Mercado, Estado, Usuario
import os
# Configuración básica de logs
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Inicia el consumidor de Kafka para recibir Calificaciones reales'

    def handle(self, *args, **options):
        # 1. Configuración de conexión a Kafka (Docker)
        kafka_server = os.environ.get('KAFKA_SERVER', 'localhost:9092')
        conf = {
            'bootstrap.servers': kafka_server,
            'group.id': 'grupo_valeska_backend',
            'auto.offset.reset': 'earliest'
        }

        self.stdout.write(self.style.WARNING(f'[INFO] Intentando conectar a Kafka en {kafka_server}...'))
        
        try:
            consumer = Consumer(conf)
            topic = 'topic-calificaciones'
            consumer.subscribe([topic])
            self.stdout.write(self.style.SUCCESS(f'[OK] CONECTADO. Escuchando mensajes en el topic: "{topic}"'))
            self.stdout.write(self.style.SUCCESS('     (Presiona Ctrl+C para detener)'))

            # 2. Ciclo Infinito de Escucha
            while True:
                msg = consumer.poll(1.0) 

                if msg is None:
                    continue 

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        # Este error es normal al inicio si el topic no existe
                        logger.warning(f"[ALERTA] El topic '{topic}' aun no existe. Esperando a que el Productor envie algo...")
                        continue
                    else:
                        logger.error(f"[ERROR] Error de Kafka: {msg.error()}")
                        continue

                # 3. ¡Mensaje Recibido!
                try:
                    raw_data = msg.value().decode('utf-8')
                    data = json.loads(raw_data)
                    
                    self.stdout.write(f"[INFO] Recibido: {data.get('instrumento', 'Sin nombre')}")
                    self.procesar_y_guardar(data)

                except json.JSONDecodeError:
                    logger.error(f"[ERROR] JSON no valido: {msg.value()}")
                except Exception as e:
                    logger.error(f"[ERROR] Procesando mensaje: {e}")

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n[STOP] Deteniendo consumidor..."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n[CRITICAL] Error de Conexion: {e}"))
        finally:
            if 'consumer' in locals():
                consumer.close()
                self.stdout.write("[INFO] Conexion cerrada.")

    def procesar_y_guardar(self, data):
        try:
            inst_obj, _ = Instrumento.objects.get_or_create(
                nombre=data.get('instrumento'),
                defaults={'tipo': 'Accion', 'moneda': 'CLP'}
            )
            mercado_obj, _ = Mercado.objects.get_or_create(
                nombre=data.get('mercado'),
                defaults={'pais': 'Chile', 'tipo': 'Bolsa'}
            )
            estado_obj, _ = Estado.objects.get_or_create(nombre='Ingresado')
            
            usuario_admin = Usuario.objects.first() 
            if not usuario_admin:
                usuario_admin = Usuario.objects.create_user('sistema', 'sis@nuam.cl', 'admin')

            nueva_calif = Calificacion.objects.create(
                monto_factor=data.get('monto', 0),
                fecha_emision=data.get('fecha_emision'),
                fecha_pago=data.get('fecha_pago'),
                instrumento=inst_obj,
                mercado=mercado_obj,
                estado=estado_obj,
                created_by=usuario_admin,
                updated_by=usuario_admin,
                usuario=usuario_admin
            )
            print(f"[DB] Guardada Calificacion ID {nueva_calif.id} para {inst_obj.nombre}")

        except Exception as e:
            print(f"[ERROR] Fallo al guardar en DB: {e}")