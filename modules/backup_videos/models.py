import os
import json
from config import Config

class BackupVideo:
    """Класс для работы с резервными видео"""
    
    def __init__(self, filename, path, description=""):
        self.filename = filename
        self.path = path
        self.description = description
        
    @staticmethod
    def get_all_videos():
        """Получение списка всех резервных видео"""
        videos = []
        
        # Проверяем существование директории
        if not os.path.exists(Config.BACKUP_VIDEOS_FOLDER):
            os.makedirs(Config.BACKUP_VIDEOS_FOLDER, exist_ok=True)
            
        # Получаем список файлов
        for filename in os.listdir(Config.BACKUP_VIDEOS_FOLDER):
            if any(filename.lower().endswith(ext) for ext in Config.ALLOWED_VIDEO_EXTENSIONS):
                path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, filename)
                
                # Получаем описание из метаданных, если есть
                description = ""
                meta_path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, f"{filename}.meta")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, 'r') as f:
                            meta = json.load(f)
                            description = meta.get('description', '')
                    except:
                        pass
                        
                videos.append(BackupVideo(filename, path, description))
                
        return videos
        
    @staticmethod
    def get_video(filename):
        """Получение информации о конкретном видео"""
        path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, filename)
        
        if not os.path.exists(path):
            return None
            
        # Получаем описание из метаданных, если есть
        description = ""
        meta_path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, f"{filename}.meta")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                    description = meta.get('description', '')
            except:
                pass
                
        return BackupVideo(filename, path, description)
        
    @staticmethod
    def save_video(file, description=""):
        """Сохранение загруженного видео"""
        if not os.path.exists(Config.BACKUP_VIDEOS_FOLDER):
            os.makedirs(Config.BACKUP_VIDEOS_FOLDER, exist_ok=True)
            
        filename = file.filename
        path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, filename)
        
        # Сохраняем файл
        file.save(path)
        
        # Сохраняем метаданные
        if description:
            meta_path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, f"{filename}.meta")
            with open(meta_path, 'w') as f:
                json.dump({'description': description}, f)
                
        return BackupVideo(filename, path, description)
        
    @staticmethod
    def delete_video(filename):
        """Удаление видео"""
        path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, filename)
        meta_path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, f"{filename}.meta")
        
        # Удаляем файл и метаданные
        if os.path.exists(path):
            os.remove(path)
            
        if os.path.exists(meta_path):
            os.remove(meta_path)
            
        return True
        
    @staticmethod
    def update_description(filename, description):
        """Обновление описания видео"""
        path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, filename)
        
        if not os.path.exists(path):
            return False
            
        # Обновляем метаданные
        meta_path = os.path.join(Config.BACKUP_VIDEOS_FOLDER, f"{filename}.meta")
        with open(meta_path, 'w') as f:
            json.dump({'description': description}, f)
            
        return True