from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Float, nullable=False)
    size_unit = db.Column(db.String(50), nullable=False, default='acres')

    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)    
    # Relate the crops with each farm
    crops = db.relationship('Crop', backref='farm', lazy=True)
class Farmer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # farmer has many farms
    farms = db.relationship('Farm', backref='farmer', lazy=True)
    crops = db.relationship('Crop', back_populates='farmer', lazy=True)

class Crop(db.Model):
    crop_id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False) # linking it to farm
    crop_name = db.Column(db.String(80), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_planted = db.Column(db.Date, default=func.now())
    quantity_harvested = db.Column(db.Float, nullable=True)  # Quantity of harvest
    stages = db.relationship('PlantStage', backref='crop', lazy=True)
    image = db.Column(db.String(200), nullable=True)  # For storing the image path
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    farmer = db.relationship('Farmer', back_populates='crops')

    # seeds = db.relationship('Seed', backref='crop', lazy=True)
    # agrochemicals = db.relationship('Agrochemical', backref='crop', lazy=True)
    # fertilizers = db.relationship('Fertilizer', backref='crop', lazy=True)
    # Foreign key to the Farmer table
       
    # Define relationship to Farmer
    

class PlantStage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)
    stage_name = db.Column(db.String(50), nullable=False)  # e.g., Planting, Transplanting
    date_recorded = db.Column(db.Date, default=func.now())  # Date of the stage

# class Seed(db.Model):
#     seed_id = db.Column(db.Integer, primary_key=True)
#     company = db.Column(db.String(100), nullable=False)
#     grade = db.Column(db.String(50), nullable=False)
#     amount = db.Column(db.Float, nullable=False)
#     transplant_date = db.Column(db.Date, default=func.now())
#     crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)


# class Agrochemical(db.Model):
#     agrochemical_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     quantity = db.Column(db.Float, nullable=False)
#     application_method = db.Column(db.String(100), nullable=True)
#     application_date = db.Column(db.Date, default=func.now())
#     crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)

# class Fertilizer(db.Model):
#     fertilizer_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     quantity = db.Column(db.Float, nullable=False)
#     application_method = db.Column(db.String(100), nullable=True)
#     application_date = db.Column(db.Date, default=func.now())
#     crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)


# class Transplant(db.Model):
#     transplant_id = db.Column(db.Integer, primary_key=True)
#     crop_type = db.Column(db.String(80), nullable=False)
#     date_transplanted = db.Column(db.Date, default=func.now())
#     number_of_heads = db.Column(db.Integer)
#     farm_size = db.Column(db.String(50))
#     fertilizer = db.Column(db.String(100))
#     fertilizer_quantity = db.Column(db.String(100))
#     farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
