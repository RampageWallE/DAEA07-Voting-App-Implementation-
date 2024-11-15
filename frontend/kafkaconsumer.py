from confluent_kafka import Consumer
import json

def consumer_recomendation(user_id):
    consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',  # Ajusta según tu configuración
        'group.id': 'recomendaciones_group',  # Grupo de consumidores
        'auto.offset.reset': 'earliest'
    })
    
    consumer.subscribe(['recomendacion'])
    
    recommendations = {}
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                break
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            data = json.loads(msg.value().decode('utf-8'))
            # Verificar si el mensaje contiene el ID del usuario
            if str(user_id) in data:
                recommendations[user_id] = data[str(user_id)]
                break
    finally:
        consumer.close()
    
    return recommendations
