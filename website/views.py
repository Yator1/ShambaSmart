from flask import Blueprint, render_template, session, redirect, url_for, flash

views = Blueprint('views', __name__)

# @views.route('/')
# def home():
#     return redirect(url_for('views.dashboard'))

@views.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'farmer_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')
