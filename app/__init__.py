from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()

def create_app(config_class=Config):
    # Create and configure the Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import main
    from app.auth.routes import auth
    from app.admin.routes import admin
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    # Context processor to make variables available in all templates
    @app.context_processor
    def inject_variables():
        from flask import request
        from app.models import SwapRequest
        
        unread_requests = 0
        if current_user.is_authenticated:
            unread_requests = SwapRequest.query.filter_by(
                receiver_id=current_user.id,
                status='pending'
            ).count()
        
        return dict(
            current_path=request.path,
            current_user_is_admin=hasattr(current_user, 'is_admin') and current_user.is_admin,
            unread_requests=unread_requests
        )

    # Error handlers
    from app.routes import not_found_error, forbidden_error, internal_error
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(500, internal_error)

    return app

# Import models at the bottom to avoid circular imports
from app import models