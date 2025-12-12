# api/producers.py
import json
import logging
import os
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        # Usamos la variable de entorno o localhost por defecto
        self.bootstrap_servers = os.environ.get('KAFKA_SERVER', 'localhost:9092')
        self.producer = None
        try:
            self.producer = Producer({'bootstrap.servers': self.bootstrap_servers})
            logger.info(f"✅ Kafka Producer conectado a {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Error conectando Kafka Producer: {e}")

    def enviar_evento(self, topic, data):
        """
        Envía un diccionario como JSON al tópico especificado.
        Manejo de errores incluido (Nicolas).
        """
        if not self.producer:
            logger.warning("⚠️ Kafka Producer no está inicializado. Omitiendo mensaje.")
            return

        try:
            # Callback para confirmar entrega
            def delivery_report(err, msg):
                if err is not None:
                    logger.error(f'❌ Fallo entrega mensaje: {err}')
                else:
                    logger.info(f'📨 Mensaje enviado a {msg.topic()} [{msg.partition()}]')

            # Serializar y enviar
            message_json = json.dumps(data)
            self.producer.produce(topic, message_json.encode('utf-8'), callback=delivery_report)
            self.producer.flush() # Forzar envío inmediato

        except Exception as e:
            logger.error(f"❌ Error enviando evento a Kafka: {e}")

# Instancia global para usar en las vistas
kafka_producer = KafkaProducer()