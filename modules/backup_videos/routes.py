from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from . import backup_videos
from .models import BackupVideo
from modules.rtmp_server.rtmp_manager import rtmp_manager
from config import Config
import os
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Проверка допустимости расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_VIDEO_EXTENSIONS

@backup_videos.route('/backup/list', methods=['GET'])
@login_required
def list_videos():
    """Получение списка всех резервных видео"""
    videos = BackupVideo.get_all_videos()
    return render_template('backup/list.html', videos=videos)

@backup_videos.route('/backup/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    """Загрузка нового резервного видео"""
    if request.method == 'POST':
        # Проверяем наличие файла в запросе
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        
        # Проверяем, что имя файла не пустое
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)
            
        # Проверяем допустимость расширения
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            description = request.form.get('description', '')
            
            # Сохраняем файл
            video = BackupVideo.save_video(file, description)
            
            flash(f'Видео "{filename}" успешно загружено')
            return redirect(url_for('backup_videos.list_videos'))
        else:
            flash('Недопустимый формат файла', 'error')
            return redirect(request.url)
            
    return render_template('backup/upload.html')

@backup_videos.route('/backup/delete/<filename>', methods=['POST'])
@login_required
def delete_video(filename):
    """Удаление резервного видео"""
    success = BackupVideo.delete_video(filename)
    
    if success:
        flash(f'Видео "{filename}" успешно удалено')
    else:
        flash(f'Ошибка при удалении видео "{filename}"', 'error')
        
    return redirect(url_for('backup_videos.list_videos'))

@backup_videos.route('/backup/set_active/<filename>', methods=['POST'])
@login_required
def set_active_video(filename):
    """Установка активного резервного видео"""
    video = BackupVideo.get_video(filename)
    
    if video:
        success = rtmp_manager.set_backup_video(video.path)
        
        if success:
            flash(f'Видео "{filename}" установлено как резервное')
            return jsonify({'success': True})
        else:
            flash(f'Ошибка при установке видео "{filename}" как резервного', 'error')
            return jsonify({'success': False}), 400
    else:
        flash(f'Видео "{filename}" не найдено', 'error')
        return jsonify({'success': False}), 404

@backup_videos.route('/backup/update/<filename>', methods=['POST'])
@login_required
def update_video_description(filename):
    """Обновление описания видео"""
    description = request.form.get('description', '')
    
    success = BackupVideo.update_description(filename, description)
    
    if success:
        flash(f'Описание видео "{filename}" обновлено')
        return jsonify({'success': True})
    else:
        flash(f'Ошибка при обновлении описания видео "{filename}"', 'error')
        return jsonify({'success': False}), 400