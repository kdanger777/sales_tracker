from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import logging
import os

db = SQLAlchemy()

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)
    leads = db.relationship('Lead', backref='shift', lazy='dynamic')
    
    def duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        else:
            return (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    notes = db.Column(db.Text, nullable=True)

def ensure_timezone_aware(dt):
    """Make sure a datetime has timezone info, adding UTC if missing."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

# Add a function to check database connectivity
def check_db_connection(app):
    """Utility function to verify database connectivity"""
    try:
        with app.app_context():
            # Try a simple query
            Shift.query.first()
            app.logger.info("Database connection successful")
            return True
    except Exception as e:
        app.logger.error(f"Database connection failed: {str(e)}")
        return False
