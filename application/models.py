from .database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    type = db.Column(db.String(), default='general')
    address = db.Column(db.String())
    pincode = db.Column(db.String())

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    occ_spots = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Integer, default=0)
    pkspots=db.relationship('ParkingSpot', backref='lot')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey(ParkingLot.id), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), default="Available", nullable=False)

class Reserve(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey(ParkingSpot.id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    vehicle_number = db.Column(db.String(), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Integer, nullable=True)
