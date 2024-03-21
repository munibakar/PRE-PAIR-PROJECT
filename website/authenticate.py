import pyrebase

config = {
'''API KEY HERE'''
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
