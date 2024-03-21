from flask import Flask, session
from flask_login import LoginManager
from firebase_admin import credentials, initialize_app, firestore, auth
from flask_session import Session

cred = credentials.Certificate('website/demo_acc.json')
firebase_app = initialize_app(cred)
db = firestore.client()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'SECRET KEY HERE'

    from .views import views
    from .auth_bp import auth_bp

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')
    return app
