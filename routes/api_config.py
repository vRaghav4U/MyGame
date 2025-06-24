from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from models import ApiConfig
import json

api_config_bp = Blueprint('api_config', __name__)

@api_config_bp.route('/')
def list_configs():
    """List all API configurations"""
    configs = ApiConfig.query.order_by(ApiConfig.created_at.desc()).all()
    return render_template('api_configs.html', configs=configs)

@api_config_bp.route('/create', methods=['GET', 'POST'])
def create_config():
    """Create new API configuration"""
    if request.method == 'POST':
        try:
            # Parse headers JSON
            headers_str = request.form.get('headers', '').strip()
            headers_dict = {}
            if headers_str:
                headers_dict = json.loads(headers_str)
            
            # Parse pagination params JSON
            pagination_params_str = request.form.get('pagination_params', '').strip()
            pagination_params_dict = {}
            if pagination_params_str:
                pagination_params_dict = json.loads(pagination_params_str)
            
            config = ApiConfig(
                name=request.form['name'],
                base_url=request.form['base_url'],
                pagination_type=request.form['pagination_type'],
                max_pages=int(request.form.get('max_pages', 100)),
                rate_limit_delay=float(request.form.get('rate_limit_delay', 1.0)),
                is_active=request.form.get('is_active') == 'on'
            )
            
            config.set_headers_dict(headers_dict)
            config.set_pagination_params_dict(pagination_params_dict)
            
            db.session.add(config)
            db.session.commit()
            
            flash(f'API configuration "{config.name}" created successfully.', 'success')
            return redirect(url_for('api_config.list_configs'))
            
        except json.JSONDecodeError as e:
            flash(f'Invalid JSON format: {str(e)}', 'error')
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error creating configuration: {str(e)}', 'error')
    
    return render_template('api_configs.html', create_mode=True)

@api_config_bp.route('/edit/<int:config_id>', methods=['GET', 'POST'])
def edit_config(config_id):
    """Edit API configuration"""
    config = ApiConfig.query.get_or_404(config_id)
    
    if request.method == 'POST':
        try:
            # Parse headers JSON
            headers_str = request.form.get('headers', '').strip()
            headers_dict = {}
            if headers_str:
                headers_dict = json.loads(headers_str)
            
            # Parse pagination params JSON
            pagination_params_str = request.form.get('pagination_params', '').strip()
            pagination_params_dict = {}
            if pagination_params_str:
                pagination_params_dict = json.loads(pagination_params_str)
            
            config.name = request.form['name']
            config.base_url = request.form['base_url']
            config.pagination_type = request.form['pagination_type']
            config.max_pages = int(request.form.get('max_pages', 100))
            config.rate_limit_delay = float(request.form.get('rate_limit_delay', 1.0))
            config.is_active = request.form.get('is_active') == 'on'
            
            config.set_headers_dict(headers_dict)
            config.set_pagination_params_dict(pagination_params_dict)
            
            db.session.commit()
            
            flash(f'API configuration "{config.name}" updated successfully.', 'success')
            return redirect(url_for('api_config.list_configs'))
            
        except json.JSONDecodeError as e:
            flash(f'Invalid JSON format: {str(e)}', 'error')
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error updating configuration: {str(e)}', 'error')
    
    # Prepare form data for editing
    config.headers_json = json.dumps(config.get_headers_dict(), indent=2)
    config.pagination_params_json = json.dumps(config.get_pagination_params_dict(), indent=2)
    
    return render_template('api_configs.html', config=config, edit_mode=True)

@api_config_bp.route('/delete/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    """Delete API configuration"""
    config = ApiConfig.query.get_or_404(config_id)
    
    try:
        config_name = config.name
        db.session.delete(config)
        db.session.commit()
        
        flash(f'API configuration "{config_name}" deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting configuration: {str(e)}', 'error')
    
    return redirect(url_for('api_config.list_configs'))

@api_config_bp.route('/toggle/<int:config_id>', methods=['POST'])
def toggle_config(config_id):
    """Toggle API configuration active status"""
    config = ApiConfig.query.get_or_404(config_id)
    
    try:
        config.is_active = not config.is_active
        db.session.commit()
        
        status = "activated" if config.is_active else "deactivated"
        flash(f'API configuration "{config.name}" {status}.', 'success')
    except Exception as e:
        flash(f'Error updating configuration: {str(e)}', 'error')
    
    return redirect(url_for('api_config.list_configs'))
