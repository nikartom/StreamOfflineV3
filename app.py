from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user
from config import Config
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация приложения Flask
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Загрузчик пользователя для Flask-Login
from modules.auth.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Импорт и регистрация модулей
from modules.auth import auth as auth_blueprint
from modules.stream_manager import stream_manager as stream_blueprint
from modules.backup_videos import backup_videos as backup_blueprint
from modules.rtmp_server import rtmp_server as rtmp_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(stream_blueprint)
app.register_blueprint(backup_blueprint)
app.register_blueprint(rtmp_blueprint)

@app.route('/')
def index():
    return redirect(url_for('stream_manager.dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)