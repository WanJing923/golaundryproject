from django.contrib import messages
from django.http import Http404
from django.shortcuts import render,redirect,get_object_or_404
import pyrebase
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from websiteapp.models import CustomUser
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from operator import itemgetter
from .models import Laundry

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
    #get data from db
    laundry_data = database.child("laundry").get().val()
    rider_data = database.child("riders").get().val()
    #sort data
    sorted_laundry_data = sorted(laundry_data.items(), key=lambda x: x[1]['registerDateTime'], reverse=True)
    sorted_rider_data = sorted(rider_data.items(), key=lambda x: x[1]['registerDateTime'], reverse=True)
    #pass
    return render(request, 'newUsers.html', {"laundry_data": sorted_laundry_data, "rider_data": sorted_rider_data})

@login_required
def newlaundrydetails(request, laundryId):
    laundry_data  = database.child("laundry").child(laundryId).get().val()
    if laundry_data is not None:
        context = {'laundry_data': laundry_data}
        return render(request, 'new-laundryDetails.html', context)
    else:
        return render(request, 'new-laundryDetails.html') 


@login_required
def newriderdetails(request):
    return render(request, 'new-riderDetails.html')






@login_required
def ratingsreports(request):
    return render(request, 'reports.html')

@login_required
def helpcentermessages(request):
    return render(request, 'helpMessage.html')

@login_required
def manageallusers(request):
    return render(request, 'all-users.html')

@login_required
def managealllaundry(request):
    return render(request, 'all-laundry.html')

@login_required
def manageallriders(request):
    return render(request, 'all-riders.html')

@login_required
def helpdetails(request):
    return render(request, 'helpDetails.html')

@login_required
def reportsdetails(request):
    return render(request, 'reportsDetails.html')

@login_required
def allusersUserDetails(request):
    return render(request, 'all-userDetails.html')

@login_required
def allusersLaundryDetails(request):
    return render(request, 'all-laundryDetails.html')

@login_required
def allusersRiderDetails(request):
    return render(request, 'all-riderDetails.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')