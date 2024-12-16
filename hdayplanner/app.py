from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure PostgreSQL database
DATABASE_URL = os.getenv('POSTGRES_URL_NON_POOLING')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Models
class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    total_budget = db.Column(db.Float, nullable=False)
    spent_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    city = db.Column(db.String(100))
    hotel = db.Column(db.String(200))
    hotel_link = db.Column(db.String(500))
    morning_activity = db.Column(db.String(500))
    morning_link = db.Column(db.String(500))
    lunch = db.Column(db.String(200))
    lunch_link = db.Column(db.String(500))
    afternoon_activity = db.Column(db.String(500))
    afternoon_link = db.Column(db.String(500))
    dinner = db.Column(db.String(200))
    dinner_link = db.Column(db.String(500))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    category = db.Column(db.String(100))
    item = db.Column(db.String(200))
    cost = db.Column(db.Float)
    date = db.Column(db.DateTime)
    notes = db.Column(db.String(500))

# Routes
@app.route('/')
def index():
    trips = Trip.query.all()  # Retrieve all trips to display on the index page
    return render_template('index.html', trips=trips)

@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if request.method == 'POST':
        data = request.json
        new_trip = Trip(
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d'),
            title=data['title'],
            total_budget=float(data['total_budget'])
        )
        db.session.add(new_trip)
        db.session.commit()

        # Create itinerary entries
        for day in data['itinerary']:
            new_itinerary = Itinerary(
                trip_id=new_trip.id,
                date=datetime.strptime(day['date'], '%Y-%m-%d'),
                city=day['city'],
                hotel=day['hotel'],
                morning_activity=day['morning_activity'],
                lunch=day['lunch'],
                afternoon_activity=day['afternoon_activity'],
                dinner=day['dinner']
            )
            db.session.add(new_itinerary)

        db.session.commit()
        return jsonify({'success': True, 'trip_id': new_trip.id})
    return render_template('trip_create.html')

@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    itineraries = Itinerary.query.filter_by(trip_id=trip_id).all()
    budgets = Budget.query.filter_by(trip_id=trip_id).all()
    
    # Calculate spent amount
    trip.spent_amount = sum(budget.cost for budget in budgets)

    return render_template('trip_details.html', trip=trip, itineraries=itineraries, budgets=budgets)

@app.route('/api/trips', methods=['POST'])
def api_create_trip():
    data = request.json
    new_trip = Trip(
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d'),
        title=data['title'],
        total_budget=float(data['total_budget'])
    )
    db.session.add(new_trip)
    db.session.commit()

    # Create default itinerary entries for each day
    start_date = new_trip.start_date
    end_date = new_trip.end_date
    current_date = start_date
    while current_date <= end_date:
        new_itinerary = Itinerary(
            trip_id=new_trip.id,
            date=current_date,
            city='',  # Default value
            hotel='',  # Default value
            hotel_link='',  # Default value
            morning_activity='',  # Default value
            morning_link='',  # Default value
            lunch='',  # Default value
            lunch_link='',  # Default value
            afternoon_activity='',  # Default value
            afternoon_link='',  # Default value
            dinner='',  # Default value
            dinner_link=''  # Default value
        )
        db.session.add(new_itinerary)
        current_date += timedelta(days=1)  # Move to the next day

    db.session.commit()

    return jsonify({'success': True, 'trip_id': new_trip.id}), 201

@app.route('/edit_trip/<int:trip_id>', methods=['GET', 'POST'])
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if request.method == 'POST':
        data = request.json
        trip.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        trip.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        trip.title = data['title']
        trip.total_budget = float(data['total_budget'])
        db.session.commit()

        # Update itinerary entries
        Itinerary.query.filter_by(trip_id=trip_id).delete()  # Clear existing itineraries
        for day in data['itinerary']:
            new_itinerary = Itinerary(
                trip_id=trip_id,
                date=datetime.strptime(day['date'], '%Y-%m-%d'),
                city=day['city'],
                hotel=day['hotel'],
                morning_activity=day['morning_activity'],
                lunch=day['lunch'],
                afternoon_activity=day['afternoon_activity'],
                dinner=day['dinner']
            )
            db.session.add(new_itinerary)

        db.session.commit()
        return jsonify({'success': True, 'trip_id': trip.id})
    return render_template('trip_create.html', trip=trip)

@app.route('/trip/<int:trip_id>/itinerary', methods=['GET', 'POST'])
def itinerary(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if request.method == 'POST':
        # Handle itinerary submission
        data = request.json
        try:
            for day in data['itinerary']:
                new_itinerary = Itinerary(
                    trip_id=trip_id,
                    date=datetime.strptime(day['date'], '%Y-%m-%d'),
                    city=day['city'],
                    hotel=day['hotel'],
                    hotel_link=day['hotel_link'],
                    morning_activity=day['morning_activity'],
                    morning_link=day['morning_link'],
                    lunch=day['lunch'],
                    lunch_link=day['lunch_link'],
                    afternoon_activity=day['afternoon_activity'],
                    afternoon_link=day['afternoon_link'],
                    dinner=day['dinner'],
                    dinner_link=day['dinner_link']
                )
                db.session.add(new_itinerary)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({'error': str(e)}), 500  # Return error message
    else:
        # Fetch existing itineraries for the trip
        itineraries = Itinerary.query.filter_by(trip_id=trip_id).all()
        return render_template('itinerary.html', trip=trip, itineraries=itineraries)

@app.route('/trip/<int:trip_id>/itinerary', methods=['POST'])
def add_itinerary(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    data = request.json  # Expecting JSON data

    try:
        for day in data['itinerary']:
            # Check if itinerary entry exists for the date
            existing_itinerary = Itinerary.query.filter_by(trip_id=trip_id, date=datetime.strptime(day['date'], '%Y-%m-%d')).first()
            if existing_itinerary:
                # Update existing itinerary
                existing_itinerary.city = day['city']
                existing_itinerary.hotel = day['hotel']
                existing_itinerary.hotel_link = day.get('hotel_link', '')
                existing_itinerary.morning_activity = day.get('morning_activity', '')
                existing_itinerary.morning_link = day.get('morning_link', '')
                existing_itinerary.lunch = day.get('lunch', '')
                existing_itinerary.lunch_link = day.get('lunch_link', '')
                existing_itinerary.afternoon_activity = day.get('afternoon_activity', '')
                existing_itinerary.afternoon_link = day.get('afternoon_link', '')
                existing_itinerary.dinner = day.get('dinner', '')
                existing_itinerary.dinner_link = day.get('dinner_link', '')
            else:
                # Create new itinerary entry
                new_itinerary = Itinerary(
                    trip_id=trip_id,
                    date=datetime.strptime(day['date'], '%Y-%m-%d'),
                    city=day['city'],
                    hotel=day['hotel'],
                    hotel_link=day.get('hotel_link', ''),
                    morning_activity=day.get('morning_activity', ''),
                    morning_link=day.get('morning_link', ''),
                    lunch=day.get('lunch', ''),
                    lunch_link=day.get('lunch_link', ''),
                    afternoon_activity=day.get('afternoon_activity', ''),
                    afternoon_link=day.get('afternoon_link', ''),
                    dinner=day.get('dinner', ''),
                    dinner_link=day.get('dinner_link', '')
                )
                db.session.add(new_itinerary)
        db.session.commit()
        return jsonify({'success': True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def trip_dashboard():
    trips = Trip.query.all()  # Retrieve all trips
    return render_template('trip_dashboard.html', trips=trips)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)