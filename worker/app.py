from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from models import db, User, News
import redis
import json

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
        redis_key = f"user:{user_id}:news_views"
        datos_brutos = r.lrange(redis_key, 0, -1)  # Obtener todos los elementos de la lista
        datos_procesados = [json.loads(item) for item in datos_brutos]  # Convertir cada item de la lista a un diccionario
        print(datos_procesados)
        
        # return datos_procesados
    except Exception as e:
        print(f'Se produjo un error: {e}')  #

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
