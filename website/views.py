from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import Farm, Crop, Farmer, PlantStage
from.forms import AddCropForm
from . import db
from .utility import allowed_file

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    farm = Farm.query.filter_by(farmer_id=current_user.id).first()
    if farm:
        crops = Crop.query.filter_by(farm_id=farm.id).all()
    else:
        crops = []
    return render_template("home.html", farm=farm, crops=crops)

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

@views.route('/add_crop/<int:farm_id>', methods=['GET', 'POST'])
def add_crop(farm_id):
    form = AddCropForm()  # Use the form from the separate file
    farm = Farm.query.get_or_404(farm_id)

    if form.validate_on_submit():
        # Log form data
        current_app.logger.info(f'Adding crop with name: {form.name.data}, variety: {form.variety.data}')

        # Saving the crop info
        crop = Crop(
            name=form.name.data,
            variety=form.variety.data,
            date_planted=form.date_planted.data,
            quantity=form.quantity.data,
            farm_id=farm_id
        )
        db.session.add(crop)
        db.session.commit()

        # Save the stage
        stage = PlantStage(
            crop_id=crop.crop_id,
            stage_name=form.stage_name.data,
            date_recorded=form.date_recorded.data
        )
        db.session.add(stage)
        db.session.commit()

        # Save image if uploaded
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(image_path)
            crop.image = filename
            db.session.commit()
        else:
            flash('Invalid file type. Only images are allowed.', 'error')
            current_app.logger.warning('Invalid file type for image upload.')

        flash('Crop added successfully', 'success')
        return redirect(url_for('views.home', farm_id=farm_id))

    return render_template('add_crop.html', form=form, farm=farm)


@views.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@views.route('/delete_crop/<int:crop_id>', methods=['POST'])
@login_required
def delete_crop(crop_id):
    try:
        crop = Crop.query.get_or_404(crop_id)
        
        # Remove the image file if it exists
        if crop.image:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], crop.image)
            if os.path.exists(image_path):
                os.remove(image_path)

        for stage in crop.stages:
            db.session.delete(stage)
        
        # Delete the crop record from the database
        db.session.delete(crop)
        db.session.commit()
        
        flash('Crop deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('views.view_farm', farm_id=crop.farm_id))

@views.route('/farm/<int:farm_id>', methods=['GET'])
def view_farm(crop_id):
    farm = Farm.query.get_or_404(crop_id)
    return render_template('view_farm.html', farm=farm)
