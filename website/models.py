from . import db
from flask_login import UserMixin

class Farmer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    crops = db.relationship('Crop', backref='farmer', lazy=True)
    transplants = db.relationship('Transplant', backref='farmer', lazy=True)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_planted = db.Column(db.Date, nullable=False)
    fertilizer = db.Column(db.String(100))
    fertilizer_quantity = db.Column(db.String(100))
    pesticide = db.Column(db.String(100))
    pesticide_quantity = db.Column(db.String(100))
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)

class Transplant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(80), nullable=False)
    date_transplanted = db.Column(db.Date, nullable=False)
    number_of_heads = db.Column(db.Integer)
    farm_size = db.Column(db.String(50))
    fertilizer = db.Column(db.String(100))
    fertilizer_quantity = db.Column(db.String(100))
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
