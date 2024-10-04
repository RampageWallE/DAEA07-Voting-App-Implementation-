from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO
import requests
import redis
from kafka import KafkaConsumer

app = Flask(__name__)

socketio = SocketIO(app)

r = redis.Redis(host='redis', port=6379, db=0)

app.secret_key = 'SECRET_KEY'

# Backend URL
BACKEND_URL = 'http://worker:5000'  # Asegúrate de que tu backend esté corriendo en este puerto

# Conexión al servidor Kafka
KAFKA_SERVER = 'kafka:9092'  # Asegúrate de que es el host y puerto correctos
KAFKA_TOPIC_TEMPLATE = "user:{user_id}:news_views"

recomendaciones_usuario = {}


def consume_kafka_messages(user_id):
    topic = KAFKA_TOPIC_TEMPLATE.format(user_id=user_id)
    
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='earliest',  # Desde el inicio del tópico
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        print(f"Mensaje recibido del tópico {topic}: {message.value}")
        recomendaciones_usuario[user_id] = recomendaciones_usuario.get(user_id, [])
        recomendaciones_usuario[user_id].append(message.value)

        socketio.emit(f'user_{user_id}_recomendaciones', message.value)



# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
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
    session.pop('user_id', None)  # Elimina el ID del usuario de la sesión
    return redirect(url_for('login'))

# Ruta para ver las noticias
@app.route('/news')
def news():
    if 'user_id' not in session:
        flash('Por favor inicia sesión.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    # Obtener lista de noticias desde el backend
    response = requests.get(f'{BACKEND_URL}/api/news')
    news_list = response.json() if response.status_code == 200 else []

    consume_kafka_messages(user_id)  # Puedes usar threading para ejecutarlo en paralelo

    
    return render_template('news.html', news_list=news_list, user_id=user_id)

# Ruta para ver el detalle de una noticia
@app.route('/news/<int:news_id>')
def news_detail(news_id):
    try :
        if 'user_id' not in session:
            flash('Por favor inicia sesión.')
            return redirect(url_for('login'))
        
        # Obtener el detalle de la noticia desde el backend
        response = requests.get(f'{BACKEND_URL}/api/news/{news_id}')

        user_id = session['user_id']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        news_detail = response.json() if response.status_code == 200 else None
        
        # Almacenar en Redis
        redis_key = f"user:{user_id}:news_views"

        print(redis_key)

        r.lpush(redis_key, json.dumps({
            'news_id': news_detail['id'],        # news_data ya es un diccionario, extraído de response.json()
            'timestamp': timestamp,
            'category': news_detail.get('category', 'Sin categoría'),  # Usamos .get() para evitar errores si falta 'category'
            'title': news_detail['title']
        }))

        alert = requests.get(f"{BACKEND_URL}/api/historial/{session['user_id']}")
        
        if news_detail:
            return render_template('news_detail.html', news=news_detail)
        else:
            flash('Noticia no encontrada.')
            return redirect(url_for('news'))
    
    except Exception as e:
        flash(f'Se produjo un error: {e}')  #

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
