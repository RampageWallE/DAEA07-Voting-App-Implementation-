from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from models import db, User, News
import redis
import json
from time import sleep 
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, col
import traceback
from manhattan import computeNearesNeighbor
import socket

try:
    from confluent_kafka import Producer, Consumer, KafkaError
    from confluent_kafka.admin import AdminClient, NewTopic
except Exception as e: 
    traceback.print_exc()

try:
    spark = SparkSession.builder \
            .appName("NewsRecommendation") \
            .master("spark://spark-master:7077") \
            .getOrCreate()
except Exception:
    print("Waiting to spark to be available..")


producer = Producer({'bootstrap.servers': 'kafka:9092',
        'client.id': socket.gethostname()})

admin_client = AdminClient({
    'bootstrap.servers': 'kafka:9092'
})



r = redis.Redis(host='redis', port=6379, db=0)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()  # Crea las tablas si no existen


def obtener_usuarios(ids):
    usuarios = {}
    for user_id in ids.keys():
        usuario = User.query.get_or_404(user_id)
        user = {
            "username":usuario.username,
            "email":usuario.email
        }
        usuarios[user_id] = user
    print(usuarios)
    return usuarios

def create_topic_if_not_exists(topic_name, num_partitions=1, replication_factor=1):
    """Crea un tópico en Kafka si no existe."""
    if not topic_exists(topic_name):
        topic_list = [NewTopic(topic=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        fs = admin_client.create_topics(topic_list)
        
        for topic, f in fs.items():
            try:
                f.result()  # Espera hasta que se complete la creación
                print(f"Tópico '{topic}' creado exitosamente.")
            except Exception as e:
                print(f"Error al crear el tópico '{topic}': {e}")
    else:
        print(f"El tópico '{topic_name}' ya existe.")


def topic_exists(topic_name):
    """Verifica si un tópico existe en Kafka."""
    topics = admin_client.list_topics(timeout=10).topics
    return topic_name in topics


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists!'}), 400
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required!'}), 400
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid email or password!'}), 401
    return jsonify({'id': user.id, 'message': 'Login successful!'}), 200


@app.route('/api/add_news', methods=['POST'])
def add_news():
    data = request.get_json()
    new_news = News(
        title=data['title'],
        content=data['content'],
        category=data['category'],  # Recibiendo la categoría
        created_at=datetime.now()
    )
    db.session.add(new_news)
    db.session.commit()
    return jsonify({'message': 'News added successfully!'}), 201

@app.route('/api/news', methods=['GET'])
def get_news():
    news_list = News.query.all()
    return jsonify([
        {
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'created_at': news.created_at,
            'views': news.views
        } for news in news_list
    ])

@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    news_item = News.query.get_or_404(news_id)
    news_item.views += 1
    db.session.commit()
    return jsonify({
        'id': news_item.id,
        'title': news_item.title,
        'content': news_item.content,
        'category': news_item.category,
        'created_at': news_item.created_at,
        'views': news_item.views
    }),200


@app.route('/api/historial/<int:user_id>', methods=['GET'])
def obtener_todos_los_topicos(user_id):
    try:
        user1 = User.query.get_or_404(user_id)
        print(user1)
        # Obtener todas las claves que coinciden con el patrón 'user:*:news_views'
        keys = r.keys('user:*:news_views')
        
        todos_los_datos = []

        for key in keys:
            user_id = key.decode('utf-8').split(':')[1]  # El formato de la clave es 'user:{user_id}:news_views'

            datos_brutos = r.lrange(key, 0, -1)

            datos_procesados = [json.loads(item) for item in datos_brutos]
            
            for dato in datos_procesados:
                dato['user_id'] = user_id  # Agregar el id del usuario a cada item de datos

            todos_los_datos.extend(datos_procesados)

        if not todos_los_datos:  # Verificar si todos_los_datos está vacío
            return {"error": "No data found"}, 404  # Retornar un mensaje de error si no hay datos

        # Crear un DataFrame de Spark con los datos obtenidos
        df = spark.createDataFrame(todos_los_datos)

        news_count_by_user = (
            df.groupBy("user_id","title")
            .agg(count("title").alias("news_count"))
        )

        # Convertir los resultados a un formato de diccionario anidado
        result = {}
        for row in news_count_by_user.collect():
            user = row['user_id']
            news = row['title']
            
            if user not in result:
                result[user] = {}
            result[user][news] = row['news_count']

        sorted_distances = computeNearesNeighbor(str(user1.id), result)[0]

        min_value = min(sorted_distances.values())

        min_keys = {key: value for key, value in sorted_distances.items() if value == min_value}
        
        # min_keys_bytes = json.dumps(min_keys).encode('utf-8')

        # usuarios = obtener_usuarios(min_keys)
        usuarios = json.dumps(obtener_usuarios(min_keys)).encode('utf-8')

        create_topic_if_not_exists(str(user1.id))

        producer.produce(topic=str(user1.id), key='recomendacion', value=usuarios)

        return usuarios, 200

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}, 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
