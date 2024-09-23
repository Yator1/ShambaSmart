from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import Farm, Crop, Farmer, PlantStage, Expense, Sale, DailyReport
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
        total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(Expense.crop_id.in_([crop.crop_id for crop in crops])).scalar() or 0
        total_sales = db.session.query(db.func.sum(Sale.total_sale)).filter(Sale.crop_id.in_([crop.crop_id for crop in crops])).scalar() or 0
        total_profit = total_sales - total_expenses
    else:
        crops = []

    crop_count = len(crops)
    return render_template("home.html", farm=farm, crops=crops, crop_count=crop_count,total_expenses=total_expenses, total_sales=total_sales, total_profit=total_profit)

@views.route('/add_farm', methods=['GET', 'POST'])
@login_required
def add_farm():
    farm = Farm.query.filter_by(farmer_id=current_user.id).first()

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

    return render_template('add_farm.html', farm=farm)

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
def view_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    return render_template('view_farm.html', farm=farm)


@views.route('/crop/<int:crop_id>', methods=['GET', 'POST'])
@login_required
def crop_detail(crop_id):
    crop = Crop.query.get_or_404(crop_id)

    farm = crop.farm

    # Fetch existing expenses and sales for this crop
    expenses = Expense.query.filter_by(crop_id=crop_id).all()
    sales = Sale.query.filter_by(crop_id=crop_id).all()

    # Calculate total expenses, total sales, and profit for this specific crop
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(crop_id=crop_id).scalar() or 0
    total_sales = db.session.query(db.func.sum(Sale.total_sale)).filter_by(crop_id=crop_id).scalar() or 0
    total_profit = total_sales - total_expenses

    if request.method == 'POST':
        # Handle adding new expense or sale
        if 'add_expense' in request.form:
            expense_type = request.form.get('expense_type')
            cost = request.form.get('cost')
            stage = request.form.get('stage')
            date_incurred_str = request.form.get('date_incurred')

            date_incurred = datetime.strptime(date_incurred_str, '%Y-%m-%d').date()

            # Add new expense
            new_expense = Expense(
                crop_id=crop_id,
                category=expense_type,
                amount=cost,
                description=stage,
                date=date_incurred
            )
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')

        elif 'add_sale' in request.form:
            amount_sold = request.form.get('amount_sold')
            price = request.form.get('price')
            date_of_sale_str = request.form.get('date_of_sale')

            total = float(price) * float(amount_sold)
            date_of_sale = datetime.strptime(date_of_sale_str, '%Y-%m-%d').date()

            # Add new sale
            new_sale = Sale(
                crop_id=crop_id,
                quantity_sold=amount_sold,
                total_sale=total,
                date=date_of_sale,
                price_per_kg=price
            )
            db.session.add(new_sale)
            db.session.commit()
            flash('Sale added successfully!', 'success')

        return redirect(url_for('views.crop_detail', crop_id=crop_id))

    return render_template('crop_detail.html', crop=crop, farm=farm, expenses=expenses, sales=sales, total_expenses=total_expenses, total_sales=total_sales, total_profit=total_profit)


@views.route('/daily_reports', methods=['GET', 'POST'])
@login_required
def daily_reports():
    farm = Farm.query.filter_by(farmer_id=current_user.id).first()
    reports = DailyReport.query.filter_by(farm_id=farm.id).all()

    if request.method == 'POST':
        report_date = datetime.strptime(request.form.get('report_date'), '%Y-%m-%d').date()
        description = request.form.get('description')

        new_report = DailyReport(date=report_date, activity=description, farm_id=farm.id)
        db.session.add(new_report)
        db.session.commit()
        flash('Daily report added successfully!', category='success')

    return render_template('daily_reports.html', farm=farm, reports=reports)

@views.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    farm = Farm.query.filter_by(farmer_id=current_user.id).first()
    crops = Crop.query.filter_by(farm_id=farm.id).all()

    if request.method == 'POST':
        crop_name = request.form.get('crop_name')
        variety = request.form.get('variety')
        quantity = request.form.get('quantity')
        date_planted = request.form.get('date_planted')

        new_crop = Crop(name=crop_name, variety=variety, quantity=quantity, date_planted=date_planted, farm_id=farm.id)
        db.session.add(new_crop)
        db.session.commit()
        flash('New crop added successfully!', category='success')

        # Add total expenses, sales, and profit for each crop
    for crop in crops:
        crop.total_expenses = crop.total_cost()
        crop.total_sales = crop.total_retail()
        crop.profit = crop.calculate_profit()

    return render_template('products.html', farm=farm, crops=crops)

@views.route('/financial_activities', methods=['GET'])
@login_required
def financial_activities():
    farm = Farm.query.filter_by(farmer_id=current_user.id).first()
    
    # Fetching all expenses and sales related to the farm
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(Expense.crop_id.in_([crop.crop_id for crop in Crop.query.filter_by(farm_id=farm.id).all()])).scalar() or 0
    total_sales = db.session.query(db.func.sum(Sale.total_sale)).filter(Sale.crop_id.in_([crop.crop_id for crop in Crop.query.filter_by(farm_id=farm.id).all()])).scalar() or 0
    total_profit = total_sales - total_expenses

    return render_template('financial_activity.html', farm=farm, total_expenses=total_expenses, total_sales=total_sales, total_profit=total_profit)


@views.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    # farm = Farm.query.filter_by(farmer_id=user.id).first()

    if request.method == 'POST':
        email = request.form.get('email')
        profile_pic = request.form.get('profile_pic')  # Optional file upload handling

        user.email = email
        if profile_pic:
            user.profile_pic = profile_pic  # Save the file appropriately

        db.session.commit()
        flash('Account details updated!', category='success')
    
    farms = user.farms

    return render_template('account.html', user=user, farm=farms)
