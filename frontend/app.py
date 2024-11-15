from datetime import datetime
import json
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO
import requests
import sys
import redis
import threading
from confluent_kafka import Consumer, KafkaError, KafkaException
from time import sleep 



from kafkaconsumer import consumer_recomendation

app = Flask(__name__)

socketio = SocketIO(app)

r = redis.Redis(host='redis', port=6379, db=0)

app.secret_key = 'SECRET_KEY'

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'frontend-group',
    'auto.offset.reset': 'latest'
})

kafka_topic = '2'


thread_running = False
kafka_thread = None

is_in_news = False
kafka_thread1 = None

# Procesa el mensaje recibido de Kafka
def process_kafka_message(message):
    try:
        # Decodifica y transforma el mensaje de Kafka
        data = json.loads(message.value().decode('utf-8'))
        
        # Envía el mensaje a los clientes conectados vía SocketIO
        socketio.emit('recommendations', data)
        print(f"Enviado a través de SocketIO: {data}")
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")

def consultar_historial_usuario(id):
    global is_in_news
    try:
        while is_in_news:
            # Verifica si el usuario está en sesión
            if not id:
                print("Usuario no autenticado. Saltando consulta de historial.")
                sleep(1)
                continue

            # Realiza la consulta al servicio `worker`
            response = requests.get(f"{BACKEND_URL}/api/historial/{id}")
            if response.status_code == 200:
                historial = response.json()
                print(f"Historial recibido: {historial}")
            else:
                print(f"Error consultando historial: {response.status_code}")
            sleep(5)
    except Exception as e:
        print(f"Error en el hilo de historial: {e}")
        


def consume_kafka(topico):
    consumer.subscribe([topico])
    try:
        while thread_running:
            msg = consumer.poll(timeout=1.0)  # Espera mensajes con un tiempo límite

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"Fin de la partición: {msg.partition()} en {msg.topic()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Procesa mensajes válidos
                process_kafka_message(msg)
    finally:
        consumer.close()

# Ejecuta el consumidor de Kafka en un hilo separado

# @app.before_request
# def activar_hilo():
#     kafka_thread = threading.Thread(target=consume_kafka)
#     kafka_thread.daemon = True
#     kafka_thread.start()

# Detener consumidor de Kafka al cerrar la aplicación
@socketio.on('disconnect')
def handle_disconnect():
    global kafka_thread
    global kafka_thread1
    # if kafka_thread.is_alive():
    #     kafka_thread.join()
    # if kafka_thread1.is_alive():
    #     kafka_thread1.join()

# Backend URL
BACKEND_URL = 'http://worker:5000'  # Asegúrate de que tu backend esté corriendo en este puerto

recomendaciones_usuario = {}

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    global thread_running
    global is_in_news
    # thread_running = False
    # is_in_news = False
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Enviar datos al backend para registrarse
        response = requests.post(f'{BACKEND_URL}/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })
        
        if response.status_code == 201:
            flash('Usuario registrado exitosamente. Inicia sesión.')
            return redirect(url_for('login'))
        else:
            flash('Error en el registro. Intenta nuevamente.')
    
    return render_template('register.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    global thread_running
    global is_in_news
    # thread_running = False
    # is_in_news = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Enviar credenciales al backend
        response = requests.post(f'{BACKEND_URL}/auth/login', json={
            'email': email,
            'password': password
        })
        
        if response.status_code == 200:
            user_data = response.json()
            session['user_id'] = user_data['id']
            flash('Login exitoso.')
            return redirect(url_for('news'))
        else:
            flash('Credenciales incorrectas. Intenta nuevamente.')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    global thread_running
    global is_in_news
    # thread_running = False
    # is_in_news = False
    session.pop('user_id', None)  # Elimina el ID del usuario de la sesión
    return redirect(url_for('login'))

# Ruta para ver las noticias
@app.route('/news')
def news():
    global thread_running
    global is_in_news
    # thread_running = False
    # is_in_news = False
    if 'user_id' not in session:
        flash('Por favor inicia sesión.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    # Obtener lista de noticias desde el backend
    response = requests.get(f'{BACKEND_URL}/api/news')
    news_list = response.json() if response.status_code == 200 else []

    return render_template('news.html', news_list=news_list, user_id=user_id)

# Ruta para ver el detalle de una noticia
@app.route('/news/<int:news_id>')
def news_detail(news_id):
    global thread_running, kafka_thread
    global is_in_news, kafka_thread1
    try:
        if 'user_id' not in session:
            flash('Por favor inicia sesión.')
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        
        if not is_in_news:
            is_in_news = True
            kafka_thread1 = threading.Thread(target=consultar_historial_usuario(id=user_id, daemon=True))
            kafka_thread1.start()

        if not thread_running:
            thread_running = True
            kafka_thread = threading.Thread(target=consume_kafka(topico=str(user_id)), daemon=True)
            kafka_thread.start()
            print("Hilo de Kafka iniciado")

        # Obtener el detalle de la noticia desde el backend
        response = requests.get(f'{BACKEND_URL}/api/news/{news_id}')

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        news_detail = response.json() if response.status_code == 200 else None
        
        # Almacenar en Redis
        redis_key = f"user:{user_id}:news_views"

        r.lpush(redis_key, json.dumps({
            'news_id': news_detail['id'],        # news_data ya es un diccionario, extraído de response.json()
            'timestamp': timestamp,
            'category': news_detail.get('category', 'Sin categoría'),  # Usamos .get() para evitar errores si falta 'category'
            'title': news_detail['title']
        }))

        # requests.get(f"{BACKEND_URL}/api/historial/{user_id}")
        
        if news_detail:
            return render_template('news_detail.html', news=news_detail)
        else:
            flash('Noticia no encontrada.')
            return redirect(url_for('news'))
    
    except Exception as e:
        flash(f'Se produjo un error: {e}')  #

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

