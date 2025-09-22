from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from config import Config

class User(UserMixin):
    """Класс для работы с пользователями"""
    
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        
    def verify_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)
        
    @staticmethod
    def get_by_username(username):
        """Получение пользователя по имени"""
        users = User.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None
        
    @staticmethod
    def get_by_id(id):
        """Получение пользователя по ID"""
        users = User.get_all_users()
        for user in users:
            if user.id == id:
                return user
        return None
        
    @staticmethod
    def get_all_users():
        """Получение списка всех пользователей"""
        users = []
        
        # Путь к файлу с пользователями
        users_file = os.path.join(Config.BASE_DIR, 'users.json')
        
        # Если файл не существует, создаем его с администратором по умолчанию
        if not os.path.exists(users_file):
            admin_password = generate_password_hash('admin')
            default_users = [
                {
                    'id': 1,
                    'username': 'admin',
                    'password_hash': admin_password
                }
            ]
            
            with open(users_file, 'w') as f:
                json.dump(default_users, f)
                
        # Загружаем пользователей из файла
        try:
            with open(users_file, 'r') as f:
                users_data = json.load(f)
                
            for user_data in users_data:
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash']
                )
                users.append(user)
                
        except Exception as e:
            # В случае ошибки возвращаем пустой список
            print(f"Error loading users: {str(e)}")
            
        return users