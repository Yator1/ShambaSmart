from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Farmer
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        farmer = Farmer.query.filter_by(username=username).first()
        
        if farmer:
            if check_password_hash(farmer.password, password):
                flash('Login successful!', category='success')
                login_user(farmer, remember=True)      

                # checking if the farmer has any associated farms
                if not farmer.farms:
                    # if no farm exists, redirect to add farm page
                    return redirect(url_for('views.add_farm'))
                # else redirect to home page         
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Login failed. Check your username.', category='error')
    return render_template('login.html', farmer=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstName = request.form.get('firstname')
        lastName = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        farmer = Farmer.query.filter_by(email=email).first()
        if farmer:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            hashed_password = generate_password_hash(password1)
            new_farmer = Farmer(first_name=firstName, last_name=lastName, email=email, username=username, password=hashed_password)
            db.session.add(new_farmer)
            db.session.commit()
            flash('Signup successful! Please log in.', category='success')

            # login the new farmer
            login_user(new_farmer, remember=True)
            flash('Account created successfully', category='success')
            return redirect(url_for('views.home'))
    return render_template('signup.html', user=current_user)
