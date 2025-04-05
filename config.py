import os

class Config:
    # Application configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sales_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
