from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_from_directory
from app import db
from models import ApiConfig, ApiResponse, CollectionJob
from services.api_client import ApiClient
from services.pagination_handler import PaginationHandler
import threading
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Dashboard showing overview of API configs and recent jobs"""
    configs = ApiConfig.query.filter_by(is_active=True).all()
    recent_jobs = CollectionJob.query.order_by(CollectionJob.start_time.desc()).limit(10).all()
    recent_responses = ApiResponse.query.order_by(ApiResponse.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         configs=configs, 
                         recent_jobs=recent_jobs,
                         recent_responses=recent_responses)

@main_bp.route('/responses')
def responses():
    """View all API responses"""
    page = request.args.get('page', 1, type=int)
    config_id = request.args.get('config_id', type=int)
    
    query = ApiResponse.query
    if config_id:
        query = query.filter_by(config_id=config_id)
    
    responses = query.order_by(ApiResponse.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    configs = ApiConfig.query.all()
    
    return render_template('responses.html', responses=responses, configs=configs, selected_config_id=config_id)

@main_bp.route('/start-collection/<int:config_id>', methods=['POST'])
def start_collection(config_id):
    """Start API data collection for a specific configuration"""
    config = ApiConfig.query.get_or_404(config_id)
    
    # Check if there's already a running job for this config
    running_job = CollectionJob.query.filter_by(
        config_id=config_id,
        status='running'
    ).first()
    
    if running_job:
        flash('A collection job is already running for this configuration.', 'warning')
        return redirect(url_for('main.index'))
    
    # Create new job
    job = CollectionJob(config_id=config_id, status='pending')
    db.session.add(job)
    db.session.commit()
    
    # Start collection in background thread
    thread = threading.Thread(target=run_collection_job, args=(job.id,))
    thread.daemon = True
    thread.start()
    
    flash(f'Started data collection for "{config.name}".', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/job-status/<int:job_id>')
def job_status(job_id):
    """Get status of a collection job"""
    job = CollectionJob.query.get_or_404(job_id)
    
    return jsonify({
        'id': job.id,
        'status': job.status,
        'progress_percentage': job.progress_percentage,
        'completed_pages': job.completed_pages,
        'total_pages': job.total_pages,
        'error_count': job.error_count,
        'error_message': job.error_message
    })

@main_bp.route('/cancel-job/<int:job_id>', methods=['POST'])
def cancel_job(job_id):
    """Cancel a running collection job"""
    job = CollectionJob.query.get_or_404(job_id)
    
    if job.status == 'running':
        job.status = 'cancelled'
        job.end_time = datetime.utcnow()
        db.session.commit()
        flash('Collection job cancelled.', 'info')
    else:
        flash('Job is not currently running.', 'warning')
    
    return redirect(url_for('main.index'))

@main_bp.route('/game')
def tic_tac_toe_game():
    """Serve the RAG Tic Tac Toe game"""
    import os
    return send_from_directory(os.getcwd(), 'game.html')

@main_bp.route('/static/images/<filename>')
def serve_image(filename):
    """Serve static images"""
    import os
    return send_from_directory(os.path.join(os.getcwd(), 'static', 'images'), filename)

def run_collection_job(job_id):
    """Run data collection job in background"""
    from app import app
    with app.app_context():
        job = CollectionJob.query.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        config = job.config
        if not config:
            logger.error(f"Config for job {job_id} not found")
            job.status = 'failed'
            job.error_message = 'Configuration not found'
            job.end_time = datetime.utcnow()
            db.session.commit()
            return
        
        try:
            job.status = 'running'
            db.session.commit()
            
            logger.info(f"Starting collection job {job_id} for config '{config.name}'")
            
            # Initialize API client
            api_client = ApiClient(
                base_url=config.base_url,
                headers=config.get_headers_dict(),
                rate_limit_delay=config.rate_limit_delay
            )
            
            # Initialize pagination handler
            pagination_handler = PaginationHandler(
                api_client=api_client,
                pagination_type=config.pagination_type,
                pagination_params=config.get_pagination_params_dict()
            )
            
            # Start pagination
            page_count = 0
            error_count = 0
            
            for page_num, success, data, response_time, error in pagination_handler.paginate(max_pages=config.max_pages):
                # Check if job was cancelled
                db.session.refresh(job)
                if job.status == 'cancelled':
                    logger.info(f"Job {job_id} was cancelled")
                    return
                
                page_count += 1
                job.total_pages = page_count
                job.completed_pages = page_count
                
                if not success:
                    error_count += 1
                    job.error_count = error_count
                
                # Create response record
                response = ApiResponse(
                    config_id=config.id,
                    page_number=page_num,
                    url=f"{config.base_url}?page={page_num}",  # Simplified URL
                    status_code=200 if success else 500,
                    response_time=response_time,
                    error_message=error
                )
                
                if success:
                    response.set_response_data_dict(data)
                
                db.session.add(response)
                db.session.commit()
                
                logger.debug(f"Processed page {page_num} for job {job_id}")
                
                # Break if too many consecutive errors
                if error_count > 5:
                    logger.error(f"Too many errors in job {job_id}, stopping")
                    job.status = 'failed'
                    job.error_message = 'Too many consecutive errors'
                    job.end_time = datetime.utcnow()
                    db.session.commit()
                    return
            
            # Job completed successfully
            job.status = 'completed'
            job.end_time = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Completed collection job {job_id}. Processed {page_count} pages with {error_count} errors")
            
        except Exception as e:
            logger.error(f"Error in collection job {job_id}: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            job.end_time = datetime.utcnow()
            db.session.commit()
