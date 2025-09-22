from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from . import rtmp_server
from .rtmp_manager import rtmp_manager
import logging

logger = logging.getLogger(__name__)

@rtmp_server.route('/rtmp/status', methods=['GET'])
@login_required
def status():
    """Получение статуса RTMP сервера"""
    return jsonify(rtmp_manager.get_status())

@rtmp_server.route('/rtmp/start/<output_name>', methods=['POST'])
@login_required
def start_stream(output_name):
    """Запуск стрима на указанную платформу"""
    success = rtmp_manager.start_stream(output_name)
    if success:
        flash(f'Стрим на {output_name} запущен успешно')
        return jsonify({'success': True})
    else:
        flash(f'Ошибка при запуске стрима на {output_name}', 'error')
        return jsonify({'success': False}), 400

@rtmp_server.route('/rtmp/stop/<output_name>', methods=['POST'])
@login_required
def stop_stream(output_name):
    """Остановка стрима на указанную платформу"""
    success = rtmp_manager.stop_stream(output_name)
    if success:
        flash(f'Стрим на {output_name} остановлен')
        return jsonify({'success': True})
    else:
        flash(f'Ошибка при остановке стрима на {output_name}', 'error')
        return jsonify({'success': False}), 400

@rtmp_server.route('/rtmp/start_all', methods=['POST'])
@login_required
def start_all_streams():
    """Запуск всех настроенных стримов"""
    success = rtmp_manager.start_all_streams()
    if success:
        flash('Все стримы запущены успешно')
        return jsonify({'success': True})
    else:
        flash('Ошибка при запуске стримов', 'error')
        return jsonify({'success': False}), 400

@rtmp_server.route('/rtmp/stop_all', methods=['POST'])
@login_required
def stop_all_streams():
    """Остановка всех активных стримов"""
    rtmp_manager.stop_all_streams()
    flash('Все стримы остановлены')
    return jsonify({'success': True})

@rtmp_server.route('/rtmp/backup/<output_name>', methods=['POST'])
@login_required
def switch_to_backup(output_name):
    """Переключение на резервное видео для указанной платформы"""
    success = rtmp_manager.switch_to_backup(output_name)
    if success:
        flash(f'Переключение на резервное видео для {output_name} выполнено успешно')
        return jsonify({'success': True})
    else:
        flash(f'Ошибка при переключении на резервное видео для {output_name}', 'error')
        return jsonify({'success': False}), 400

@rtmp_server.route('/rtmp/monitor/start', methods=['POST'])
@login_required
def start_monitoring():
    """Запуск мониторинга входящего потока"""
    success = rtmp_manager.start_monitoring()
    if success:
        flash('Мониторинг стрима запущен')
        return jsonify({'success': True})
    else:
        flash('Ошибка при запуске мониторинга', 'error')
        return jsonify({'success': False}), 400

@rtmp_server.route('/rtmp/monitor/stop', methods=['POST'])
@login_required
def stop_monitoring():
    """Остановка мониторинга"""
    success = rtmp_manager.stop_monitoring()
    if success:
        flash('Мониторинг стрима остановлен')
        return jsonify({'success': True})
    else:
        flash('Мониторинг не был запущен', 'warning')
        return jsonify({'success': False}), 400