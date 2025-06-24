import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from routes.main import main_bp
from routes.api_config import api_config_bp

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(api_config_bp, url_prefix='/api')

# This is the entry point for Vercel
def handler(request):
    return app(request.environ, lambda *args: None)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)