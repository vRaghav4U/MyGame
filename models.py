from app import db
from datetime import datetime
from sqlalchemy import Text, JSON
import json

class ApiConfig(db.Model):
    __tablename__ = 'api_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(500), nullable=False)
    headers = db.Column(Text)  # JSON string
    pagination_type = db.Column(db.String(50), nullable=False)  # 'page', 'cursor', 'offset'
    pagination_params = db.Column(Text)  # JSON string for additional pagination params
    max_pages = db.Column(db.Integer, default=100)
    rate_limit_delay = db.Column(db.Float, default=1.0)  # seconds between requests
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to responses
    responses = db.relationship('ApiResponse', backref='api_config', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_headers_dict(self):
        """Parse headers JSON string to dictionary"""
        if self.headers:
            try:
                return json.loads(self.headers)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_headers_dict(self, headers_dict):
        """Set headers from dictionary"""
        self.headers = json.dumps(headers_dict) if headers_dict else None
    
    def get_pagination_params_dict(self):
        """Parse pagination params JSON string to dictionary"""
        if self.pagination_params:
            try:
                return json.loads(self.pagination_params)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_pagination_params_dict(self, params_dict):
        """Set pagination params from dictionary"""
        self.pagination_params = json.dumps(params_dict) if params_dict else None

class ApiResponse(db.Model):
    __tablename__ = 'api_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('api_configs.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_data = db.Column(Text)  # JSON string of response
    error_message = db.Column(Text)
    response_time = db.Column(db.Float)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_response_data_dict(self):
        """Parse response data JSON string to dictionary"""
        if self.response_data:
            try:
                return json.loads(self.response_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_response_data_dict(self, data_dict):
        """Set response data from dictionary"""
        self.response_data = json.dumps(data_dict) if data_dict else None

class CollectionJob(db.Model):
    __tablename__ = 'collection_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('api_configs.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    total_pages = db.Column(db.Integer, default=0)
    completed_pages = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    error_message = db.Column(Text)
    
    # Relationship to config
    config = db.relationship('ApiConfig', backref='jobs')
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_pages == 0:
            return 0
        return (self.completed_pages / self.total_pages) * 100
