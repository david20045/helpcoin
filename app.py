# app.py

import os
from flask import Flask, request, jsonify
from models import db, User, Task, UserTask
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Настройка базы данных через переменную окружения DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///helpcoin.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    # Добавление задач, если их еще нет
    if Task.query.count() == 0:
        task1 = Task(title="Сбор мусора в парке", description="Соберите 10 кг мусора в парке Центральный.", reward=10)
        task2 = Task(title="Помощь пожилым соседям", description="Помогите пожилым соседям с покупкой продуктов.", reward=15)
        task3 = Task(title="Уборка снега с подъезда", description="Уберите снег с подъезда вашего дома.", reward=20)
        db.session.add_all([task1, task2, task3])
        db.session.commit()

# Эндпоинты
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    telegram_id = data.get('telegram_id')
    username = data.get('username')

    if not telegram_id:
        return jsonify({'error': 'Telegram ID is required'}), 400

    user = User.query.filter_by(telegram_id=telegram_id).first()
    if user:
        return jsonify({'message': 'User already registered'}), 200

    user = User(telegram_id=telegram_id, username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    tasks_list = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'reward': task.reward
    } for task in tasks]
    return jsonify(tasks_list), 200

@app.route('/api/accept_task', methods=['POST'])
def accept_task():
    data = request.json
    user_id = data.get('user_id')
    task_id = data.get('task_id')

    user = User.query.filter_by(telegram_id=user_id).first()
    task = Task.query.get(task_id)

    if not user or not task:
        return jsonify({'error': 'User or Task not found'}), 404

    existing = UserTask.query.filter_by(user_id=user.id, task_id=task.id).first()
    if existing:
        return jsonify({'error': 'Task already accepted'}), 400

    user_task = UserTask(user_id=user.id, task_id=task.id)
    db.session.add(user_task)
    db.session.commit()

    return jsonify({'message': 'Task accepted'}), 200

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    user_id = data.get('user_id')
    task_id = data.get('task_id')

    user = User.query.filter_by(telegram_id=user_id).first()
    task = Task.query.get(task_id)

    if not user or not task:
        return jsonify({'error': 'User or Task not found'}), 404

    user_task = UserTask.query.filter_by(user_id=user.id, task_id=task.id, status='pending').first()
    if not user_task:
        return jsonify({'error': 'Task not found or already completed'}), 404

    # Для упрощения предполагаем, что задача выполнена
    user_task.status = 'completed'
    user_task.completed_at = datetime.utcnow()
    user.tokens += task.reward
    db.session.commit()

    return jsonify({'message': 'Task completed and tokens awarded'}), 200

@app.route('/api/user_tasks/<int:telegram_id>', methods=['GET'])
def get_user_tasks(telegram_id):
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user_tasks = UserTask.query.filter_by(user_id=user.id).all()
    tasks_list = [{
        'task_id': ut.task.id,
        'title': ut.task.title,
        'status': ut.status
    } for ut in user_tasks]
    return jsonify(tasks_list), 200

@app.route('/api/profile/<int:telegram_id>', methods=['GET'])
def get_profile(telegram_id):
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    profile = {
        'username': user.username,
        'tokens': user.tokens,
        'created_at': user.created_at.strftime('%d-%m-%Y')
    }
    return jsonify(profile), 200

if __name__ == "__main__":
    app.run(debug=True)