from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from . import db  
from flask_login import login_user, login_required, logout_user, current_user
import pyrebase
from firebase_admin import credentials, auth
from flask_session import Session

config = {
    'apiKey': "AIzaSyBUVGM_OnNbu_K8lLykM5T-Tu31mIUAgkw",
    'authDomain': "prepair-demo.firebaseapp.com",
    'projectId': "prepair-demo",
    'storageBucket': "prepair-demo.appspot.com",
    'messagingSenderId': "718275532446",
    'appId': "1:718275532446:web:0f85dd84fb87cc83fd0d8f",
    'measurementId': "G-3DLX53HNSV",
    'databaseURL' : ''
}

firebase = pyrebase.initialize_app(config)
auth_firebase = firebase.auth()
auth_bp = Blueprint('auth', __name__)

def create_or_update_user(email, username, password, is_google=False):
    user_query = db.collection('users').where('username', '==', username).limit(1)
    existing_user = user_query.get()

    if not existing_user:
        try:
            if not is_google:
                user = auth_firebase.create_user_with_email_and_password(email, password)
            else:
                # Handle Google login differently or update existing user data
                user = {'localId': 'google'}  # Dummy user for Google login

            user_data = {
                'email': email,
                'username': username
            }

            user_ref = db.collection('users').document(user['localId'])
            user_ref.set(user_data)

            flash('Registration successful!', 'success')
            return True

        except Exception as e:
            if 'WEAK_PASSWORD' in str(e):
                flash('Password is too weak. Choose a stronger password.', 'error')
            elif 'EMAIL_EXISTS' in str(e):
                flash('Email address already exists. Try another email.', 'error')
            else:
                flash('Registration failed. Please try again.', 'error')
    else:
        flash('Username already exists.', 'error')
        return False

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password_1 = request.form.get('password1')
        password_2 = request.form.get('password2')
        username = request.form.get('username')
        id_token = request.form.get('id_token')

        if id_token:
            # Handle Google login
            decoded_token = auth_firebase.verify_id_token(id_token)
            email = decoded_token['email']
            username = decoded_token['name']

        if password_1 == password_2:
            create_or_update_user(email, username, is_google=bool(id_token))

    return render_template('sign_up.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('views.main_page', user='user'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        id_token = request.form.get('id_token')

        if id_token:
            # Handle Google login
            decoded_token = auth_firebase.verify_id_token(id_token)
            email = decoded_token['email']
            username = decoded_token['name']
            create_or_update_user(email, username, is_google=True)

        try:
            user = auth_firebase.sign_in_with_email_and_password(email, password)

            user_ref = db.collection('users').where('email', '==', email).limit(1)
            user_doc = user_ref.get()

            username = user_doc[0].get('username')
            session['user'] = username
            return redirect(url_for('views.main_page'))

        except Exception as e:
            flash('Failed to login.', 'error')

    return render_template('login.html')

@login_required
@auth_bp.route('/logout')
def logout():
    session.pop('user')
    flash('You have been logged out.', 'success')
    return redirect(url_for('views.home_page'))
