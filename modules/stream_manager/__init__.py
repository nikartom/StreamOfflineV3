from flask import Blueprint

stream_manager = Blueprint('stream_manager', __name__)

from . import routes