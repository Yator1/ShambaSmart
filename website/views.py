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
        size_unit = request.form.get('size_unit')

        new_farm = Farm(name=farm_name, country=country, address=address, size=size, size_unit=size_unit, farmer_id=current_user.id)
        db.session.add(new_farm)
        db.session.commit()
        flash('Farm added successfully', category='success')
        return redirect(url_for('views.home'))

    return render_template('add_farm.html')

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    farm = Farm.query.filter_by(farmer_id=current_user.id).first()
    return render_template("home.html", farm=farm)

@views.route('/crop_record')
def crop_records():
    return render_template('crop_records.html')

@views.route('/view_crop')
def view_crop():
    return render_template('view_crop.html')

# edit information 
@views.route('/edit_farm/<int:farm_id>', methods=['GET', 'POST'])
@login_required
def edit_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    
    if request.method == 'POST':
        farm.name = request.form.get('name')
        farm.country = request.form.get('country')
        farm.address = request.form.get('address')
        farm.size = request.form.get('size')
        farm.size_unit = request.form.get('size_unit')

        db.session.commit()
        flash('Farm information updated successfully', category='success')
        return redirect(url_for('views.home'))

    return render_template('edit_farm.html', farm=farm)
