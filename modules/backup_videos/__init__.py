from flask import Blueprint

backup_videos = Blueprint('backup_videos', __name__)

from . import routes, models