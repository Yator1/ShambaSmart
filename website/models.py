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
    quantity_unit = db.Column(db.String(50), nullable=False, default='grams')
    date_planted = db.Column(db.Date, default=func.now())
    quantity_harvested = db.Column(db.Float, nullable=True)  # Quantity of harvest
    stages = db.relationship('PlantStage', backref='crop', lazy=True)
    image = db.Column(db.String(200), nullable=True)  # For storing the image path
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    farmer = db.relationship('Farmer', back_populates='crops')
    expenses = db.relationship('Expense', back_populates='crop', lazy=True)
    sales = db.relationship('Sale', back_populates='crop', lazy=True)

    def total_cost(self):
        """Calculate total expenses for this crop"""
        return sum(expense.amount for expense in self.expenses)

    def total_retail(self):
        """Calculate total sales for this crop"""
        return sum(sale.total_sale for sale in self.sales)
    
    def calculate_profit(self):
        """Calculate the profit for this crop"""
        return self.total_retail() - self.total_cost()
    
    def update_quantity_harvested(self):
        self.quantity_harvested = sum(sale.quantity_sold for sale in self.sales)
        db.session.commit()

class PlantStage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)
    stage_name = db.Column(db.String(50), nullable=False, default='Planting')  # e.g., Planting, Transplanting
    date_recorded = db.Column(db.Date, default=func.now())  # Date of the stage


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date of the expense
    description = db.Column(db.String(255), nullable=False)  # What the expense was for
    amount = db.Column(db.Float, nullable=False)  # Cost of the expense
    category = db.Column(db.String(50), nullable=False)  # Labor, fertilizer, etc.

    crop = db.relationship('Crop', back_populates='expenses')


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date of the sale
    quantity_sold = db.Column(db.Float, nullable=False)  # Quantity sold
    price_per_kg = db.Column(db.Float, nullable=False)  # Price per kg
    total_sale = db.Column(db.Float, nullable=False)  # Total sale = quantity_sold * price_per_kg

    crop = db.relationship('Crop', back_populates='sales')


class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'), nullable=True)  # Optional crop
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    activity = db.Column(db.String(255), nullable=False)

    crop = db.relationship('Crop', backref='daily_reports', lazy=True)
    farm = db.relationship('Farm', backref='daily_reports', lazy=True)