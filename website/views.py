from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Crop
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if 'farmer_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('home.html')

@views.route('/crop_record')
def crop_records():
    return render_template('crop_records.html')

@views.route('/view_crop')
def view_crop():
    return render_template('view_crop.html')