import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Config:
    # Основные настройки приложения
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Пути к директориям
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    BACKUP_VIDEOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'backup_videos')
    
    # Настройки RTMP
    RTMP_SERVER_PORT = int(os.environ.get('RTMP_SERVER_PORT') or 1935)
    RTMP_APP_NAME = os.environ.get('RTMP_APP_NAME') or 'live'
    
    # Настройки для мониторинга
    STREAM_CHECK_INTERVAL = int(os.environ.get('STREAM_CHECK_INTERVAL') or 5)  # в секундах
    
    # Максимальный размер загружаемого файла (10 ГБ)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024
    
    # Разрешенные расширения для загрузки видео
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'flv'}
    
    @staticmethod
    def init_app(app):
        # Создание необходимых директорий
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.BACKUP_VIDEOS_FOLDER, exist_ok=True)