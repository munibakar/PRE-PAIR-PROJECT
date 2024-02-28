#from flask_login import UserMixin
from firebase_admin import firestore
from flask_login import UserMixin, LoginManager

db = firestore.client()

class User(UserMixin): # PROGRAMDA ŞU ANLIK BU CLASS KULLANILMIYOR 
    pass

    @staticmethod
    def get(user_id):
       
        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        return User(user_data['id'])
        