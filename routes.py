from flask import render_template, request, jsonify
from datetime import datetime, timezone
from models import db, Shift, Lead

def init_routes(app):
    @app.route('/')
    def index():
        active_shift = Shift.query.filter_by(end_time=None).first()
        return render_template('index.html', active_shift=active_shift)

    @app.route('/api/shift/start', methods=['POST'])
    def start_shift():
        # Check if there's already an active shift
        active_shift = Shift.query.filter_by(end_time=None).first()
        if (active_shift):
            return jsonify({'error': 'Already have an active shift'}), 400
        
        new_shift = Shift()
        db.session.add(new_shift)
        db.session.commit()
        
        return jsonify({
            'shift_id': new_shift.id,
            'start_time': new_shift.start_time.isoformat()
        })

    @app.route('/api/shift/end', methods=['POST'])
    def end_shift():
        shift_id = request.json.get('shift_id')
        if not isinstance(shift_id, int):
            return jsonify({'error': 'Invalid shift_id'}), 400
        
        shift = Shift.query.get(shift_id)
        if not shift:
            return jsonify({'error': 'Invalid or missing shift_id'}), 400
        
        if shift.end_time is not None:
            return jsonify({'error': 'Shift already ended'}), 400
        
        shift.end_time = datetime.now(timezone.utc)
        db.session.commit()
        
        # The 'duration' value represents the total time of the shift in seconds.
        return jsonify({
            'shift_id': shift.id,
            'duration': shift.duration()
        })

    @app.route('/api/lead/add', methods=['POST'])
    def add_lead():
        shift_id = request.json.get('shift_id')
        notes = request.json.get('notes', '')
        
        shift = Shift.query.get(shift_id)
        if not shift or shift.end_time:
            return jsonify({'error': 'Invalid shift'}), 400
        
        lead = Lead(shift_id=shift_id, notes=notes, timestamp=datetime.now(timezone.utc))
        db.session.add(lead)
        db.session.commit()
        
        return jsonify({
            'lead_id': lead.id,
            'timestamp': lead.timestamp.isoformat()
        })

    @app.route('/api/stats')
    def get_stats():
        # Get all completed shifts
        shifts = Shift.query.filter(Shift.end_time != None).all()
        
        if not shifts:
            return jsonify({
                'avg_leads_per_shift': 0,
                'avg_time_per_lead': 0,
                'total_leads': 0,
                'total_shifts': 0,
                'time_distribution': {hour: 0 for hour in range(24)},
                'shifts': []
            })
        
        total_shifts = len(shifts)
        total_leads = sum(shift.leads.count() for shift in shifts)
        total_duration = sum(shift.duration() for shift in shifts)
        
        # Calculate metrics with proper error handling
        avg_leads_per_shift = total_leads / total_shifts if total_shifts > 0 else 0
        avg_time_per_lead = total_duration / total_leads if total_leads > 0 else 0
        
        # Add logging
        app.logger.debug(f"Total duration: {total_duration}, Total leads: {total_leads}")
        app.logger.debug(f"Avg time per lead: {avg_time_per_lead}")
        
        # Calculate time distribution
        all_leads = Lead.query.all()
        lead_hours = [lead.timestamp.hour for lead in all_leads]
        time_distribution = {hour: lead_hours.count(hour) for hour in range(24)}
        
        # Format shift data for charts
        shift_data = []
        for shift in shifts:
            lead_count = shift.leads.count()
            shift_data.append({
                'id': shift.id,
                'start_time': shift.start_time.isoformat(),
                'end_time': shift.end_time.isoformat() if shift.end_time else None,
                'duration': shift.duration(),
                'lead_count': lead_count
            })
        
        return jsonify({
            'avg_leads_per_shift': avg_leads_per_shift,
            'avg_time_per_lead': avg_time_per_lead,
            'total_leads': total_leads,
            'total_shifts': total_shifts,
            'time_distribution': time_distribution,
            'shifts': shift_data
        })

    @app.route('/api/shift/active')
    def get_active_shift():
        active_shift = Shift.query.filter_by(end_time=None).first()
        
        if not active_shift:
            return jsonify({"active_shift": None})
        
        # Fix: Make start_time timezone-aware before subtracting
        start_time = active_shift.start_time
        if start_time.tzinfo is None:
            # Convert naive datetime to timezone-aware
            start_time = start_time.replace(tzinfo=timezone.utc)
        
        # Now both datetimes are timezone-aware
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Get leads for this shift
        leads_data = []
        for lead in active_shift.leads:
            leads_data.append({
                "id": lead.id,
                "timestamp": lead.timestamp.isoformat()
            })
        
        return jsonify({
            "active_shift": {
                "id": active_shift.id,
                "start_time": active_shift.start_time.isoformat(),
                "elapsed_seconds": elapsed,
                "leads": leads_data
            }
        })
