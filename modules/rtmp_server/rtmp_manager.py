import os
import signal
import subprocess
import time
import logging
import threading
import psutil
from config import Config

logger = logging.getLogger(__name__)

class RTMPManager:
    """
    Класс для управления RTMP потоками с использованием FFmpeg
    """
    def __init__(self):
        self.input_stream = None
        self.output_streams = {}
        self.ffmpeg_processes = {}
        self.stream_status = {
            'input': False,
            'outputs': {}
        }
        self.backup_video = None
        self.monitor_thread = None
        self.stop_monitor = threading.Event()
        
    def set_input_stream(self, url):
        """Установка входящего потока"""
        self.input_stream = url
        logger.info(f"Input stream set to: {url}")
        
    def add_output_stream(self, name, url):
        """Добавление выходящего потока"""
        self.output_streams[name] = url
        self.stream_status['outputs'][name] = False
        logger.info(f"Added output stream {name}: {url}")
        
    def remove_output_stream(self, name):
        """Удаление выходящего потока"""
        if name in self.output_streams:
            del self.output_streams[name]
            if name in self.stream_status['outputs']:
                del self.stream_status['outputs'][name]
            if name in self.ffmpeg_processes:
                self.stop_stream(name)
                del self.ffmpeg_processes[name]
            logger.info(f"Removed output stream: {name}")
            
    def set_backup_video(self, video_path):
        """Установка резервного видео"""
        if os.path.exists(video_path):
            self.backup_video = video_path
            logger.info(f"Backup video set to: {video_path}")
            return True
        else:
            logger.error(f"Backup video file not found: {video_path}")
            return False
            
    def start_stream(self, output_name):
        """Запуск стрима на указанную платформу"""
        if not self.input_stream:
            logger.error("No input stream defined")
            return False
            
        if output_name not in self.output_streams:
            logger.error(f"Output stream {output_name} not found")
            return False
            
        output_url = self.output_streams[output_name]
        
        # Формирование команды FFmpeg
        command = [
            'ffmpeg',
            '-i', self.input_stream,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'flv',
            output_url
        ]
        
        try:
            # Запуск процесса FFmpeg
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.ffmpeg_processes[output_name] = process
            self.stream_status['outputs'][output_name] = True
            logger.info(f"Started streaming to {output_name}: {output_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream to {output_name}: {str(e)}")
            return False
            
    def start_all_streams(self):
        """Запуск всех настроенных стримов"""
        success = True
        for output_name in self.output_streams:
            if not self.start_stream(output_name):
                success = False
        return success
        
    def stop_stream(self, output_name):
        """Остановка стрима на указанную платформу"""
        if output_name in self.ffmpeg_processes:
            process = self.ffmpeg_processes[output_name]
            
            # Корректное завершение процесса FFmpeg
            if process.poll() is None:  # Процесс еще работает
                try:
                    # Сначала пробуем мягкое завершение
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Если не завершился за 5 секунд, убиваем жестко
                    process.kill()
                    
            self.stream_status['outputs'][output_name] = False
            del self.ffmpeg_processes[output_name]
            logger.info(f"Stopped streaming to {output_name}")
            return True
        else:
            logger.warning(f"No active stream to {output_name}")
            return False
            
    def stop_all_streams(self):
        """Остановка всех активных стримов"""
        output_names = list(self.ffmpeg_processes.keys())
        for output_name in output_names:
            self.stop_stream(output_name)
            
    def switch_to_backup(self, output_name):
        """Переключение на резервное видео для указанной платформы"""
        if not self.backup_video:
            logger.error("No backup video defined")
            return False
            
        if output_name not in self.output_streams:
            logger.error(f"Output stream {output_name} not found")
            return False
            
        # Останавливаем текущий стрим
        if output_name in self.ffmpeg_processes:
            self.stop_stream(output_name)
            
        output_url = self.output_streams[output_name]
        
        # Формирование команды FFmpeg для стриминга резервного видео
        command = [
            'ffmpeg',
            '-re',  # Чтение с нативной скоростью
            '-stream_loop', '-1',  # Бесконечный цикл
            '-i', self.backup_video,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'flv',
            output_url
        ]
        
        try:
            # Запуск процесса FFmpeg
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.ffmpeg_processes[output_name] = process
            self.stream_status['outputs'][output_name] = True
            logger.info(f"Switched to backup video for {output_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching to backup for {output_name}: {str(e)}")
            return False
            
    def start_monitoring(self):
        """Запуск мониторинга входящего потока"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            logger.warning("Monitoring already running")
            return False
            
        self.stop_monitor.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_stream)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Stream monitoring started")
        return True
        
    def stop_monitoring(self):
        """Остановка мониторинга"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_monitor.set()
            self.monitor_thread.join(timeout=5)
            logger.info("Stream monitoring stopped")
            return True
        return False
        
    def _monitor_stream(self):
        """Функция мониторинга входящего потока"""
        check_interval = Config.STREAM_CHECK_INTERVAL
        
        while not self.stop_monitor.is_set():
            # Проверка состояния входящего потока
            input_active = self._check_input_stream()
            self.stream_status['input'] = input_active
            
            # Если входящий поток пропал, переключаемся на резервное видео
            if not input_active and self.backup_video:
                logger.warning("Input stream lost, switching to backup video")
                for output_name in self.output_streams:
                    if output_name in self.ffmpeg_processes:
                        self.switch_to_backup(output_name)
            
            # Проверка состояния выходящих потоков
            for output_name, process in list(self.ffmpeg_processes.items()):
                if process.poll() is not None:  # Процесс завершился
                    logger.warning(f"Stream to {output_name} has stopped unexpectedly")
                    self.stream_status['outputs'][output_name] = False
                    del self.ffmpeg_processes[output_name]
            
            time.sleep(check_interval)
            
    def _check_input_stream(self):
        """Проверка доступности входящего потока"""
        if not self.input_stream:
            return False
            
        # Используем FFprobe для проверки потока
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=codec_type',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            '-select_streams', 'v:0',  # Выбираем первый видеопоток
            '-i', self.input_stream
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,  # Таймаут 5 секунд
                universal_newlines=True
            )
            
            # Если FFprobe вернул "video", значит поток активен
            return "video" in result.stdout
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
            
    def get_status(self):
        """Получение текущего статуса всех потоков"""
        return self.stream_status

# Создаем глобальный экземпляр менеджера
rtmp_manager = RTMPManager()