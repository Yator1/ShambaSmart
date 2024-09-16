from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Float, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)

    farmer = db.relationship('Farmer', backref='farms')
class Farmer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    crops = db.relationship('Crop', backref='farmer', lazy=True)
    # transplants = db.relationship('Transplant', backref='farmer', lazy=True)

class Crop(db.Model):
    crop_id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_planted = db.Column(db.Date, default=func.now())
    harevest_date = db.Column(db.Date, default=func.now())
    # fertilizer = db.Column(db.String(100))
    # fertilizer_quantity = db.Column(db.String(100))
    # pesticide = db.Column(db.String(100))
    # pesticide_quantity = db.Column(db.String(100))
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    seeds = db.relationship('Seed', backref='crop', lazy=True)
    agrochemicals = db.relationship('Agrochemical', backref='crop', lazy=True)
    fertilizers = db.relationship('Fertilizer', backref='crop', lazy=True)

class Seed(db.Model):
    # Data for the seed
    seed_id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transplant_date = db.Column(db.Date, default=func.now())
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)


class Agrochemical(db.Model):
    # Data for the chemical pesticides
    agrochemical_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    application_method = db.Column(db.String(100), nullable=True)
    application_date = db.Column(db.Date, default=func.now())
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)


class Fertilizer(db.Model):
    # Data for the fertilizers
    fertilizer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    application_method = db.Column(db.String(100), nullable=True)
    application_date = db.Column(db.Date, default=func.now())
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)

# class Transplant(db.Model):
#     transplant_id = db.Column(db.Integer, primary_key=True)
#     crop_type = db.Column(db.String(80), nullable=False)
#     date_transplanted = db.Column(db.Date, default=func.now())
#     number_of_heads = db.Column(db.Integer)
#     farm_size = db.Column(db.String(50))
#     fertilizer = db.Column(db.String(100))
#     fertilizer_quantity = db.Column(db.String(100))
#     farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
