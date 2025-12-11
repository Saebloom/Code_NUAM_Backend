from confluent_kafka import Producer
import json

conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

datos = {
    "instrumento": "FALABELLA",
    "mercado": "Bolsa de Santiago",
    "monto": 2100.50,
    "fecha_emision": "2024-01-15",
    "fecha_pago": "2024-01-20"
}

print(f"📨 Enviando dato: {datos['instrumento']}")
producer.produce('topic-calificaciones', value=json.dumps(datos))
producer.flush()
print(" ¡Mensaje enviado a Kafka!")