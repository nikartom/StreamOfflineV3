from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from . import stream_manager
from modules.rtmp_server.rtmp_manager import rtmp_manager
from modules.backup_videos.models import BackupVideo
import logging

logger = logging.getLogger(__name__)

@stream_manager.route('/dashboard')
@login_required
def dashboard():
    """Главная панель управления стримом"""
    # Получаем статус всех потоков
    stream_status = rtmp_manager.get_status()
    
    # Получаем список резервных видео
    backup_videos = BackupVideo.get_all_videos()
    
    return render_template('stream/dashboard.html', 
                          stream_status=stream_status,
                          backup_videos=backup_videos)

@stream_manager.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Настройки стрима"""
    if request.method == 'POST':
        # Обновление настроек входящего потока
        input_stream = request.form.get('input_stream')
        if input_stream:
            rtmp_manager.set_input_stream(input_stream)
            flash('Настройки входящего потока обновлены')
            
        # Обновление настроек выходящих потоков
        output_names = request.form.getlist('output_name')
        output_urls = request.form.getlist('output_url')
        
        # Удаляем все существующие выходящие потоки
        for name in list(rtmp_manager.output_streams.keys()):
            rtmp_manager.remove_output_stream(name)
            
        # Добавляем новые выходящие потоки
        for name, url in zip(output_names, output_urls):
            if name and url:
                rtmp_manager.add_output_stream(name, url)
                
        flash('Настройки выходящих потоков обновлены')
        return redirect(url_for('stream_manager.dashboard'))
        
    # Получаем текущие настройки
    input_stream = rtmp_manager.input_stream
    output_streams = rtmp_manager.output_streams
    
    return render_template('stream/settings.html',
                          input_stream=input_stream,
                          output_streams=output_streams)

@stream_manager.route('/status/update', methods=['GET'])
@login_required
def status_update():
    """AJAX-эндпоинт для обновления статуса стрима"""
    return jsonify(rtmp_manager.get_status())