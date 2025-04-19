import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from app import create_app
from models import db, Shift, Lead

fake = Faker()

def seed_data():
    """Populate the database with fake shifts and leads for testing."""
    app = create_app()
    
    with app.app_context():
        # Clear existing data from the tables (adjust as needed for your DB)
        db.session.execute("DELETE FROM lead")
        db.session.execute("DELETE FROM shift")
        db.session.commit()
        
        print("Creating fake completed shifts with leads...")
        # Create 5 completed shifts with associated leads
        for _ in range(5):
            # Start a shift sometime in the past 1-10 days, lasting 1-4 hours
            shift_start = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 10), hours=random.randint(1, 5))
            shift_end = shift_start + timedelta(hours=random.randint(1, 4))
            shift = Shift(start_time=shift_start, end_time=shift_end)
            db.session.add(shift)
            db.session.commit()  # Commit to generate an ID for the shift
            
            # Generate a random number of leads (5 to 20) during the shift
            num_leads = random.randint(5, 20)
            for _ in range(num_leads):
                # Assign lead timestamp within shift period
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
        
        # Generate a few leads (3 to 10) for the active shift
        num_leads = random.randint(3, 10)
        for _ in range(num_leads):
            lead_time = active_shift_start + timedelta(minutes=random.randint(0, 60))
            lead = Lead(shift_id=active_shift.id, timestamp=lead_time, notes=fake.sentence())
            db.session.add(lead)
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()