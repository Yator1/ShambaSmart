from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import Farm, Crop, Farmer, PlantStage
from datetime import datetime
# from.forms import AddCropForm
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

    crop_count = len(crops)
    return render_template("home.html", farm=farm, crops=crops, crop_count=crop_count)

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
    farm = Farm.query.get_or_404(farm_id)

    if request.method == 'POST':
        crop_name = request.form.get('name')
        variety = request.form.get('variety')
        date_planted_str = request.form.get('date_planted')
        quantity = request.form.get('quantity')
        quantity_unit = request.form.get('quantity_unit')
        stage_name = request.form.get('stage_name')
        date_recorded_str = request.form.get('date_recorded')
        image_file = request.files.get('image')  # Handle image upload from HTML form

        if not crop_name or not variety:
            flash('Please provide all the required fields.', 'error')
            return redirect(url_for('views.add_crop', farm_id=farm_id))

        try:
            # converting date strings to obj
            date_planted = datetime.strptime(date_planted_str, '%Y-%m-%d').date() if date_planted_str else None
            date_recorded = datetime.strptime(date_recorded_str, '%Y-%m-%d').date() if date_recorded_str else None

            # Save crop details
            crop = Crop(
                crop_name=crop_name,
                variety=variety,
                date_planted=date_planted,
                quantity=quantity,
                quantity_unit=quantity_unit,
                farm_id=farm_id,
                farmer_id=farm_id
            )
            db.session.add(crop)
            db.session.flush()  # Flush to generate the crop ID

            # Save the plant stage
            stage = PlantStage(
                crop_id=crop.crop_id,
                stage_name=stage_name,
                date_recorded=date_recorded
            )
            db.session.add(stage)
            db.session.commit()

            # Handle image upload if provided
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)  # Save image to the server
                crop.image = filename  # Save image filename to crop model
                db.session.commit()  # Commit image filename to the database
                current_app.logger.info(f"Image uploaded: {filename}")
            elif image_file:
                flash('Invalid file type. Only images are allowed.', 'error')

            flash('Crop added successfully', 'success')
            return redirect(url_for('views.home', farm_id=farm_id))

        except Exception as e:
            current_app.logger.error(f"Error adding crop: {e}")
            db.session.rollback()
            flash('An error occurred while adding the crop.', 'error')

    return render_template('add_crop.html', farm=farm)



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
