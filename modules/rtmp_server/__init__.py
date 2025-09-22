from flask import Blueprint

rtmp_server = Blueprint('rtmp_server', __name__)

from . import routes, rtmp_manager