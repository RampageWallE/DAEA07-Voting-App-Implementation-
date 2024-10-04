from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from models import db, User, News
import redis
import json
from kafka import KafkaProducer


from pyspark.sql import SparkSession


spark = SparkSession.builder.appName("NewsRecommendation").master("spark://spark:8080").getOrCreate()

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],  # Cambia si tu puerto o servicio de Kafka es diferente
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializar los mensajes en JSON
)

r = redis.Redis(host='redis', port=6379, db=0)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()  # Crea las tablas si no existen

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
    news_item.views += 1  # Incrementar contador de vistas
    db.session.commit()  # Guardar el incremento
    return jsonify({
        'id': news_item.id,
        'title': news_item.title,
        'content': news_item.content,
        'category': news_item.category,
        'created_at': news_item.created_at,
        'views': news_item.views
    })


@app.route('/api/historial/<int:user_id>', methods=['GET'])
def obtener_datos_usuario(user_id):
    try:
        # https://github.com/RampageWallE/DAEAlab08.git
        redis_key = f"user:*:news_views"
        all_keys = r.lrange(redis_key, 0, -1)  # Obtener todos los elementos de la lista

        todos_los_datos = []

        for key in all_keys:
            datos_brutos = r.lrange(key, 0, -1)  # Obtener los elementos de la lista
            datos_procesados = [json.loads(item) for item in datos_brutos]  # Convertir cada item a un diccionario
            todos_los_datos.extend(datos_procesados)          

        
        recomendaciones = procesar_datos_con_spark(todos_los_datos, user_id)

        topic = f"user:{user_id}:news_views"
        producer.send(topic, recomendaciones)
        producer.flush() 

        return {"recomendaciones": recomendaciones}

        # return datos_procesados
    except Exception as e:
        print(f'Se produjo un error: {e}') 


def procesar_datos_con_spark(datos, user_id):
    # Convertir los datos a un DataFrame de Spark
    df = spark.createDataFrame(datos)

    # Realizar un conteo de las categorías de noticias vistas por otros usuarios
    # Excluyendo los datos del usuario actual
    df_filtrado = df.filter(df['user_id'] != user_id)

    # Contar cuántas veces se ha visto cada categoría
    categorias_populares = df_filtrado.groupBy('category').count().orderBy('count', ascending=False)

    # Seleccionar las 3 categorías más populares
    top_categorias = categorias_populares.limit(3).collect()

    # Convertir el resultado a una lista de diccionarios
    top_categorias_json = [row.asDict() for row in top_categorias]

    # Para cada categoría popular, obtener noticias recomendadas
    recomendaciones = []
    for categoria in top_categorias_json:
        # Filtrar noticias de esa categoría que aún no haya visto el usuario
        noticias_recomendadas = df.filter((df['category'] == categoria['category']) & (df['user_id'] != user_id)) \
                                  .select('news_id', 'title', 'category').distinct().limit(5).collect()
        
        recomendaciones.extend([row.asDict() for row in noticias_recomendadas])

    return recomendaciones

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
