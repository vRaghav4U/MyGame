import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__, 
           static_folder=os.path.join(parent_dir, 'static'),
           template_folder=os.path.join(parent_dir, 'templates'))

app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database with fallback
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///temp.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Import and register routes
sys.path.insert(0, os.path.join(parent_dir, 'routes'))
from main import main_bp
from api_config import api_config_bp

app.register_blueprint(main_bp)
app.register_blueprint(api_config_bp, url_prefix='/api')

# Initialize database
with app.app_context():
    sys.path.insert(0, parent_dir)
    import models
    try:
        db.create_all()
    except:
        pass  # Ignore database errors in serverless