import pyrebase

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
auth = firebase.auth()