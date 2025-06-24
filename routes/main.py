from flask import Blueprint, send_from_directory
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the Tic Tac Toe game as main page"""
    return send_from_directory(os.getcwd(), 'game.html')

@main_bp.route('/static/images/<filename>')
def serve_image(filename):
    """Serve static images"""
    return send_from_directory(os.path.join(os.getcwd(), 'static', 'images'), filename)