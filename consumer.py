import sys
from confluent_kafka import Consumer, KafkaError, KafkaException

# Variable global para controlar la ejecución
running = True

# Función que procesa el mensaje
def msg_process(msg):
    print(f"{msg.value().decode('utf-8')}")
    # Puedes agregar más lógica de procesamiento aquí

# Función principal de consumo de mensajes
def basic_consume_loop(consumer, topics):
    global running  # Usar la variable global

    try:
        # Suscribir al tópico
        consumer.subscribe(topics)

        while running:
            # Espera hasta 1 segundo para recibir un mensaje
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue  # Si no hay mensaje, continúa esperando

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Evento de fin de partición
                    sys.stderr.write(f'%% {msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
                elif msg.error():
                    # Ocurrió otro error
                    raise KafkaException(msg.error())
            else:
                # Si no hay error, procesa el mensaje
                msg_process(msg)
    finally:
        # Cierra el consumidor de forma correcta
        consumer.close()

# Función para detener el consumo
def shutdown():
    global running
    running = False

# Configurar el consumidor
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',  # Dirección del broker de Kafka
    'group.id': 'news',
    'enable.auto.commit': 'false',        # ID del grupo de consumidores
    'auto.offset.reset': 'latest'         # Empieza desde el inicio si no hay offset previo
})

# Llamada a la función para consumir mensajes del tópico 'recomendacion'
basic_consume_loop(consumer, ['2'])  # Cambia 'recomendacion' por tu tópico
