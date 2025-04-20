import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from app import create_app
from models import db, Shift, Lead
from sqlalchemy import text

fake = Faker()

def seed_data():
    """Populate the database with fake shifts and leads for testing,
    ensuring a maximum of 1 shift per day. Each completed shift lasts approx. 3.5 to 4.2 hours,
    biased towards 4 hours."""
    app = create_app()
    
    with app.app_context():
        # Clear existing data from the tables
        db.session.execute(text("DELETE FROM lead"))
        db.session.execute(text("DELETE FROM shift"))
        db.session.commit()
        
        print("Creating fake completed shifts with leads...")
        for _ in range(5):
            # Start a shift sometime in the past 1-10 days, at a random hour between 6 and 14.
            base_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10))
            start_hour = random.randint(6, 14)
            shift_start = base_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            
            # Set shift duration between 3.5 to 4.2 hours with a bias towards 4 hours.
            shift_length_hours = random.triangular(3.5, 4.2, 4.0)
            shift_end = shift_start + timedelta(hours=shift_length_hours)
            
            shift = Shift(start_time=shift_start, end_time=shift_end)
            db.session.add(shift)
            db.session.commit()  # Commit to generate an ID for the shift

            # Generate a random number of leads for the shift using triangular distribution
            # with daily goal of 15 and an upper cap of 20 leads.
            num_leads = min(int(random.triangular(5, 21, 15)), 20)
            for _ in range(num_leads):
                total_minutes = int((shift_end - shift_start).total_seconds() // 60)
                lead_time = shift_start + timedelta(minutes=random.randint(0, total_minutes))
                lead = Lead(shift_id=shift.id, timestamp=lead_time, notes=fake.sentence())
                db.session.add(lead)
            db.session.commit()
        
        print("Creating one active shift with leads...")
        # Create one active shift (no end_time) with a few leads
        active_shift_start = datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 3))
        active_shift = Shift(start_time=active_shift_start, end_time=None)
        db.session.add(active_shift)
        db.session.commit()
        
        # Generate a few leads for the active shift using a similar distribution:
        num_leads = min(int(random.triangular(3, 21, 15)), 20)
        for _ in range(num_leads):
            lead_time = active_shift_start + timedelta(minutes=random.randint(0, 60))
            lead = Lead(shift_id=active_shift.id, timestamp=lead_time, notes=fake.sentence())
            db.session.add(lead)
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()