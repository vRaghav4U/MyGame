# API Pagination Manager

## Overview

This is a Flask-based web application designed to manage and execute paginated API data collection. The system provides a web interface for configuring various API endpoints with different pagination strategies (page-based, offset-based, cursor-based) and automatically collects data while respecting rate limits.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.1 with Python 3.11
- **Database**: SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production)
- **WSGI Server**: Gunicorn for production deployment
- **Middleware**: ProxyFix for handling reverse proxy headers

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's built-in templating)
- **CSS Framework**: Bootstrap with Replit's dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS with Bootstrap components

### Database Design
- **ApiConfig**: Stores API endpoint configurations including pagination settings, headers, and rate limiting
- **ApiResponse**: Stores collected API response data (referenced but not fully implemented)
- **CollectionJob**: Tracks background data collection tasks (referenced but not implemented)

## Key Components

### Models (`models.py`)
- **ApiConfig**: Main configuration entity with JSON serialization for headers and pagination parameters
- **ApiResponse**: Placeholder for storing API response data
- Helper methods for JSON parsing and serialization of configuration parameters

### Services
- **ApiClient** (`services/api_client.py`): HTTP client with rate limiting and session management
- **PaginationHandler** (`services/pagination_handler.py`): Handles different pagination strategies (page, offset, cursor)

### Routes
- **Main Blueprint** (`routes/main.py`): Dashboard, response viewing, and collection management
- **API Config Blueprint** (`routes/api_config.py`): CRUD operations for API configurations

### Templates
- **Base Template**: Bootstrap-based layout with dark theme and navigation
- **Dashboard**: Overview of configurations and recent activity
- **API Configs**: Management interface for API endpoint configurations
- **Responses**: Data viewing interface with filtering capabilities

## Data Flow

1. **Configuration Creation**: Users create API configurations through the web interface, specifying endpoints, pagination type, headers, and rate limits
2. **Data Collection**: Background jobs use the ApiClient and PaginationHandler to fetch data from configured APIs
3. **Response Storage**: API responses are stored in the database with metadata
4. **Data Viewing**: Users can view collected data through the web interface with filtering options

## External Dependencies

### Python Packages
- **Flask**: Web framework and core functionality
- **Flask-SQLAlchemy**: Database ORM and migrations
- **Gunicorn**: Production WSGI server
- **psycopg2-binary**: PostgreSQL database adapter
- **email-validator**: Email validation utilities
- **requests**: HTTP client library (implied dependency)

### Frontend Dependencies
- **Bootstrap**: CSS framework via CDN (Replit dark theme variant)
- **Font Awesome**: Icon library via CDN
- **Bootstrap JavaScript**: Interactive components

### Infrastructure
- **PostgreSQL**: Production database (configured in .replit)
- **SQLite**: Development database fallback

## Deployment Strategy

### Production Deployment
- **Platform**: Replit Autoscale deployment target
- **Server**: Gunicorn with bind to 0.0.0.0:5000
- **Database**: PostgreSQL with connection pooling and health checks
- **Environment**: Production secrets managed through environment variables

### Development Environment
- **Local Server**: Flask development server with debug mode
- **Database**: SQLite for local development
- **Hot Reload**: Gunicorn with --reload flag for development workflow

### Configuration Management
- **Session Secret**: Environment variable with fallback for development
- **Database URL**: Environment variable with SQLite fallback
- **Connection Pooling**: 300-second recycle with pre-ping health checks

## Recent Changes
- June 24, 2025: Initial project setup with complete Flask API pagination manager
- June 24, 2025: Fixed threading issue in background job processing
- June 24, 2025: Application successfully deployed and running

## Changelog
- June 24, 2025. Initial setup complete with working application

## User Preferences

Preferred communication style: Simple, everyday language.