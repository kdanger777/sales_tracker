import os
from flask import Flask
import logging
from dotenv import load_dotenv
from models import db
from routes import init_routes
from config import Config

load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Use environment variables for configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sales_tracker.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register routes
    init_routes(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
