from django.contrib import messages
from django.shortcuts import render,redirect
import pyrebase
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from websiteapp.models import CustomUser
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect

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
auth = firebase.auth()
database=firebase.database()

def register(request):
    if request.method == 'POST':
        email_address = request.POST.get('email_address')
        password = request.POST.get('password')

        try:
            user = auth.create_user_with_email_and_password(email_address, password) 
            custom_user = CustomUser.objects.create(email_address=email_address, firebase_uid=user['localId'])
            messages.success(request, 'Admin registered successfully.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Failed to register admin: ' + str(e))
    return render(request, 'register.html')


# Create your views here.
def login_admin(request):
    if request.method == 'POST':
        email_address = request.POST.get('emailAddress')
        password = request.POST.get('password')

        try:
            firebase_user_id = auth.sign_in_with_email_and_password(email_address, password)['localId']

            # Perform a mapping to a Django user or create a new user if necessary
            try:
                user = CustomUser.objects.get(firebase_uid=firebase_user_id)
            except CustomUser.DoesNotExist:
                messages.error(request, 'Failed to login: ' + str(e))
            login(request, user)
            return redirect('newusers')

        except Exception as e:
            error_message = str(e)
            messages.error(request, error_message)

    return render(request, 'login.html')

@login_required
def newusers(request):
    return render(request, 'newUsers.html')

def ratingsreports(request):
    return render(request, 'reports.html')

def helpcentermessages(request):
    return render(request, 'helpMessage.html')

def manageallusers(request):
    return render(request, 'all-users.html')

def managealllaundry(request):
    return render(request, 'all-laundry.html')

def manageallriders(request):
    return render(request, 'all-riders.html')

def newlaundrydetails(request):
    return render(request, 'new-laundryDetails.html')

def newriderdetails(request):
    return render(request, 'new-riderDetails.html')

def helpdetails(request):
    return render(request, 'helpDetails.html')

def reportsdetails(request):
    return render(request, 'reportsDetails.html')

def allusersUserDetails(request):
    return render(request, 'all-userDetails.html')

def allusersLaundryDetails(request):
    return render(request, 'all-laundryDetails.html')

def allusersRiderDetails(request):
    return render(request, 'all-riderDetails.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')