from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'thisIsMySecretKey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///rideshare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# initialize extensions 
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# MODELS 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.Float, default=5.0)
    total_ratings = db.Column(db.Integer, default=0)
    bitcoin_address = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # add the relationships
    driver_rides = db.relationship('Ride', backref='driver', lazy=True, foreign_keys='Ride.driver_id')
    bookings = db.relationship('Booking', backref='passenger', lazy=True)


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    origin = db.Column(db.String(200), unique=True, nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price_fiat = db.Column(db.Float, nullable=False)
    price_bitcoin = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # add the relationships
    bookings = db.relationship('Booking', backref='passenger', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False) 
    payment_status = db.Column(db.String(20), default='pending') 
    bitcoin_tx_hash = db.Column(db.String(100))
    total_amount_fiat = db.Column(db.Float)
    total_amount_bitcoin = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) 
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        phone_number=data.get('phone_number'),
        bitcoin_address=data.get('bitcoin_address')
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'rating': user.rating,
                'bitcoin_address': user.bitcoin_address
            }
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

# Ride Management Routes
@app.route('/api/rides', methods=['GET'])
def get_rides():
    rides = Ride.query.filter_by(status='active').all()
    rides_list = []
    
    for ride in rides:
        rides_list.append({
            'id': ride.id,
            'driver': ride.driver.username,
            'origin': ride.origin,
            'destination': ride.destination,
            'departure_time': ride.departure_time.isoformat(),
            'available_seats': ride.available_seats,
            'price_fiat': ride.price_fiat,
            'price_bitcoin': ride.price_bitcoin,
            'description': ride.description,
            'driver_rating': ride.driver.rating
        })
    
    return jsonify(rides_list)

@app.route('/api/rides', methods=['POST'])
@jwt_required()
def create_ride():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    ride = Ride(
        driver_id=user_id,
        origin=data['origin'],
        destination=data['destination'],
        departure_time=datetime.fromisoformat(data['departure_time']),
        available_seats=data['available_seats'],
        price_fiat=data['price_fiat'],
        price_bitcoin=data['price_bitcoin'],
        description=data.get('description', '')
    )
    
    db.session.add(ride)
    db.session.commit()
    
    return jsonify({'message': 'Ride created successfully', 'ride_id': ride.id}), 201

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def book_ride():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    ride = Ride.query.get(data['ride_id'])
    if not ride or ride.available_seats < data['seats_booked']:
        return jsonify({'message': 'Ride not available or insufficient seats'}), 400
    
    # Calculate total amount
    if data['payment_method'] == 'bitcoin':
        total_amount = ride.price_bitcoin * data['seats_booked']
        total_amount_bitcoin = total_amount
        total_amount_fiat = None
    else:
        total_amount = ride.price_fiat * data['seats_booked']
        total_amount_fiat = total_amount
        total_amount_bitcoin = None
    
    booking = Booking(
        ride_id=data['ride_id'],
        passenger_id=user_id,
        seats_booked=data['seats_booked'],
        payment_method=data['payment_method'],
        total_amount_fiat=total_amount_fiat,
        total_amount_bitcoin=total_amount_bitcoin
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'message': 'Booking created successfully',
        'booking_id': booking.id,
        'total_amount': total_amount,
        'payment_method': data['payment_method']
    }), 201

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'rating': user.rating,
        'total_ratings': user.total_ratings,
        'bitcoin_address': user.bitcoin_address
    })

@app.route('/api/my-rides', methods=['GET'])
@jwt_required()
def get_my_rides():
    user_id = get_jwt_identity()
    rides = Ride.query.filter_by(driver_id=user_id).all()
    
    rides_list = []
    for ride in rides:
        rides_list.append({
            'id': ride.id,
            'origin': ride.origin,
            'destination': ride.destination,
            'departure_time': ride.departure_time.isoformat(),
            'available_seats': ride.available_seats,
            'price_fiat': ride.price_fiat,
            'price_bitcoin': ride.price_bitcoin,
            'status': ride.status,
            'bookings_count': len(ride.bookings)
        })
    
    return jsonify(rides_list)

@app.route('/api/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(passenger_id=user_id).all()
    
    bookings_list = []
    for booking in bookings:
        bookings_list.append({
            'id': booking.id,
            'ride': {
                'origin': booking.ride.origin,
                'destination': booking.ride.destination,
                'departure_time': booking.ride.departure_time.isoformat(),
                'driver': booking.ride.driver.username
            },
            'seats_booked': booking.seats_booked,
            'payment_method': booking.payment_method,
            'payment_status': booking.payment_status,
            'total_amount_fiat': booking.total_amount_fiat,
            'total_amount_bitcoin': booking.total_amount_bitcoin
        })
    
    return jsonify(bookings_list)

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)