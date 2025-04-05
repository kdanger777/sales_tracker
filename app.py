from flask import Flask
import logging
from models import db
from routes import init_routes
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
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
    app.run(debug=True)
