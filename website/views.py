from difflib import get_close_matches
from sys import prefix
from weakref import ref
from flask import Flask, Blueprint, jsonify, render_template, request, flash, redirect, session, url_for
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from firebase_admin import  firestore
from flask_wtf import FlaskForm
from httplib2 import Credentials
from requests import post
from wtforms.validators import InputRequired, EqualTo
from firebase_admin import auth
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from firebase_admin import firestore
import firebase_admin
import random
import json


views = Blueprint('views', __name__)

@views.route("/") # Site linkine tıklandığında açılacak olan sayfa bu.
def home_page():
    return render_template('index.html')

@views.route("/main") # Kullanıcı giriş yaptıktan sonra bu sayfa açılacak.
def main_page():
    username = session['user']
    user_ref = db.collection('users').where('username', '==', username).limit(1)
    user_docs = user_ref.get()

    if not user_docs:
        return []

    user_data = user_docs[0].to_dict()
    user_games = user_data.get('games', [])
    # Kullanıcının oyun isimlerini içerecek liste
    user_game_names = [game.get('name', '') for game in user_games]

# Şimdi user_game_names listesini kullanabilirsiniz
    print(user_game_names)
    
    other_users_ref = db.collection('users').stream()

    matching_users_dict = {}
    for other_user in other_users_ref:
        other_user_data = other_user.to_dict()

        # Skip the logged-in user
        if other_user_data['username'] != username:
            other_user_games = other_user_data.get('games', [])

            # Check if any game matches with the logged-in user's games
            for game in other_user_games:
                if any(user_game['name'] == game['name'] for user_game in user_games):
                    # Add the username and game to the dictionary
                    matching_users_dict.setdefault(other_user_data['username'], []).append(game['name'])

    # Now matching_users_dict contains usernames as keys and a list of games as values
    print(matching_users_dict)    
    return render_template('user_home.html', user_data = matching_users_dict)


# Firestore bağlantısı
db = firestore.client()
@views.route('/Profile', methods = ['GET', 'POST'])
def profile():
    random_number = random.randint(1, 1000)
    if 'user' in session:
        username = session['user']
        
        # Firestore sorgusu ile kullanıcının verilerini çekme
        user_ref = db.collection('users').where('username', '==', username).limit(1)
        user_doc = user_ref.get()
    
        if user_doc:
            user_data = user_doc[0].to_dict()
            
            return render_template('Profile.html', user_data=user_data,random_number = random_number)
        else:
            # Kullanıcı belgesi bulunamadıysa başka bir işlem yapabilirsiniz
            return render_template('Profile.html', error_message='Kullanıcı bulunamadı.')
        
@views.route('/search-and-add-games', methods = ['GET', 'POST'])
def add_game():
    random_user = []
    other_users_ref = db.collection('users').stream()
    for other_user in other_users_ref:
        other_user_data = other_user.to_dict()

        # Giriş yapan kullanıcı hariç diğer kullanıcıların oyunlarını al
        random_user.append(other_user_data["username"])
        
    random_user = json.dumps(random_user)
        
    
    if 'user' in session:
        username = session['user']
        # Firestore sorgusu ile kullanıcının verilerini çekme
        user_query = db.collection('users').where('username', '==', username).limit(1)
        user_docs = user_query.get()

        if user_docs:
            user_data = user_docs[0].to_dict()

            if request.method == 'POST':
                games = request.json.get('selectedGames')             

                # Check if the user already has games
                if 'games' in user_data:
                    # If games exist, append new games to the existing list if they are not already present
                    for game in games:
                        # Check if the game is not already in the list
                        if all(existing_game['name'] != game for existing_game in user_data['games']):
                            user_data['games'].append({'name': game, 'hours': random.randint(1, 1000)})
                else:
                    # If no games exist, directly assign the games as a list of dictionaries
                    user_data['games'] = [{'name': game, 'hours': random.randint(1, 1000)} for game in games] if games else ''
                    
                    
                
                
                # Now, get the specific document reference for the user
                user_ref = db.collection('users').document(user_docs[0].id)

                if user_ref.update({'games': user_data['games']}):
                    print("buraya girdin")
                    # Flash message for success
                    

                    # Redirect to the profile page
                    

    return render_template('add_game.html',random_user = random_user)


    
@views.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user' in session:
        username = session['user']
        
        # Firestore sorgusu ile kullanıcının verilerini çekme
        user_ref = db.collection('users').where('username', '==', username).limit(1)
        user_doc = user_ref.get()
    
        if user_doc:
            user_data = user_doc[0].to_dict()

    return render_template('change_password.html',user_data=user_data)


db = firestore.client()

@views.route('/search', methods=['GET'])
def search():
    # Get the username from the search bar
    query = request.args.get('username')

    # Perform Firestore query
    results = perform_firestore_query(query)

    return render_template('search_results.html', results=results)

@views.route('/search_results_p/<username>', methods = ['GET', 'POST'])
def search_results_p(username):
    # Perform Firestore query to get user profile
    user_query = db.collection('users').where('username', '==', username).limit(1)
    user_docs = user_query.get()
    # Process query results
    user_data = user_docs[0].to_dict() if user_docs else None
    
    if request.method == 'POST':
        flash('Message sent succesfully.', 'success')

    return render_template('search_results_p.html', user_data=user_data)

def perform_firestore_query(prefix):
    # Firestore'dan tüm kullanıcı adlarını alın
    all_usernames = [doc.get('username') for doc in db.collection('users').stream()]

    # Kullanıcının girdiği terime benzer kullanıcı adlarını bulun
    close_matches = get_close_matches(prefix, all_usernames, n=10, cutoff=0.6)

    if not close_matches:
        # close_matches boşsa veya geçerli değilse, hata mesajı ver veya uygun bir değer ata
        return []

    # Firestore sorgusu için benzer kullanıcı adlarını kullanın
    user_query = db.collection('users').where('username', 'in', close_matches)
    user_docs = user_query.get()

    # Firestore sorgusu sonuçlarını işleyin
    results = [doc.to_dict() for doc in user_docs]

    return results
