from django.shortcuts import render
import pyrebase

config={
    "apiKey": "AIzaSyBTIjB4Zz60jlnjVRNBeLEc8YDOVjsErRU",
    "authDomain": "golaundry-906c7.firebaseapp.com",
    "databaseURL": "https://golaundry-906c7-default-rtdb.firebaseio.com",
    "projectId": "golaundry-906c7",
    "storageBucket": "golaundry-906c7.appspot.com",
    "messagingSenderId": "63734818081",
    "appId": "1:63734818081:web:24fa422edc2802ac47ca60",
    "measurementId": "G-2000030N7P"
}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()

# Create your views here.
def login(request):
    return render(request, 'login.html')
