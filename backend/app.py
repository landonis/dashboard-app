
#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dashboard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
db.init_app(app)
jwt.init_app(app)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# Authentication decorators
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def user_or_admin_required(f):
    @wraps(f)
    @jwt_required()    
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role not in ['user', 'admin']:
            return jsonify({'error': 'User access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        user = User.query.filter_by(username=username).first()

        if user:
            logger.info(f"Input password: {password}")
            logger.info(f"Hash from DB: {user.password_hash}")

        if user and user.check_password(password):
            logger.info(f"User {username} logged in successfully, creating access token")
            access_token = create_access_token(identity=str(user.id))
            
            return jsonify({
                'token': access_token,
                'user': user.to_dict()
            })
        else:
            logger.warning(f"Failed login attempt for user {username}")
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logout successful'})

@app.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user:
            return jsonify(user.to_dict())
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500

@app.route('/users', methods=['GET'])
@admin_required
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500

@app.route('/users', methods=['POST'])
@admin_required
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        user = User(username=username, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User {username} created successfully")
        return jsonify(user.to_dict()), 201

    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'username' in data:
            # Check if username already exists for another user
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'role' in data:
            user.role = data['role']
        
        db.session.commit()
        logger.info(f"User {user.username} updated successfully")
        return jsonify(user.to_dict())

    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user'}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        username = user.username
        
        db.session.delete(user)
        db.session.commit()
        
        logger.info(f"User {username} deleted successfully")
        return jsonify({'message': 'User deleted successfully'})

    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/users/<int:user_id>/change-password', methods=['POST'])
@admin_required
def change_password(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        new_password = data.get('password')

        if not new_password:
            return jsonify({'error': 'Password required'}), 400

        user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"Password changed for user {user.username}")
        return jsonify({'message': 'Password changed successfully'})

    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500

# Import and register module routes
from modules.system_info.api import system_info_bp
app.register_blueprint(system_info_bp, url_prefix='/api/modules')
#try:

#    logger.info("System info module loaded successfully")
#except ImportError as e:
 #   logger.error(f"Failed to load system info module: {str(e)}")
#except Exception as e:
 #   logger.error(f"Error registering system info module: {str(e)}")

# Health check endpoint

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Database initialization
def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            # Create default admin user if not exists
            if not User.query.filter_by(username='admin').first():
                admin_user = User(username='admin', role='admin')
                admin_user.set_password('admin')
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Default admin user created")
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            sys.exit(1)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


init_db()
if __name__ == '__main__':
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
