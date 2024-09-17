from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Farm
from . import db
views = Blueprint('views', __name__)


@views.route('/add_farm', methods=['GET', 'POST'])
def add_farm():
    if request.method == 'POST':
        farm_name = request.form.get('name')
        country = request.form.get('country')
        address = request.form.get('address')
        size = request.form.get('size')

        new_farm = Farm(name=farm_name, country=country, address=address, size=size, farmer_id=current_user.id)
        db.session.add(new_farm)
        db.session.commit()
        flash('Farm added successfully', category='success')
        return redirect(url_for('views.home'))

    return render_template('add_farm.html')

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    
    return render_template("home.html")

@views.route('/crop_record')
def crop_records():
    return render_template('crop_records.html')

@views.route('/view_crop')
def view_crop():
    return render_template('view_crop.html')