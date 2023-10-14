from django.contrib import messages
from django.shortcuts import render,redirect
import pyrebase
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from websiteapp.models import CustomUser
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from datetime import datetime

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
def newriderdetails(request, riderId):
    rider_data  = database.child("riders").child(riderId).get().val()
    if rider_data is not None:
        context = {'rider_data': rider_data}
        return render(request, 'new-riderDetails.html', context)
    else:
        return render(request, 'new-riderDetails.html') 
    
@login_required
def ratingsreports(request):
    reports_data = database.child("reports").get().val()
    reports_with_user_and_role_data = []

    for report_id, report_info in reports_data.items():
        user_id = report_info["userId"]
        reporter_role = report_info["reporterRole"]
        reporter_id = report_info["reporterId"]

        user_data = database.child("users").child(user_id).get().val()

        reporterAll_data = None

        if reporter_role == "laundry":
            # Fetch laundry data using the reporterId
            reporterAll_data = database.child("laundry").child(reporter_id).get().val()
        else:
            # Fetch rider data using the reporterId
            reporterAll_data = database.child("riders").child(reporter_id).get().val()

        if user_data and reporterAll_data:
            report_with_data = {
                "report_id": report_id,
                "report_info": report_info,
                "user_data": user_data,
                "reporterAll_data": reporterAll_data,
            }

            reports_with_user_and_role_data.append(report_with_data)

    sorted_reports_with_data = sorted(reports_with_user_and_role_data, key=lambda x: x["report_info"]["currentDateTime"], reverse=True)

    context = {"reports_data": sorted_reports_with_data}
    return render(request, 'reports.html', context)

@login_required
def reportsdetails(request, reportId):
    report_details_data  = database.child("reports").child(reportId).get().val()
    if report_details_data is not None:
        reporter_role = report_details_data.get("reporterRole")
        reporter_id = report_details_data.get("reporterId")
        user_id = report_details_data.get("userId")
        order_id = report_details_data.get("orderId")
        rate_id = report_details_data.get("rateId")
        
        if reporter_role == "laundry":
            reporter_data = database.child("laundry").child(reporter_id).get().val()
            user_data = database.child("users").child(user_id).get().val()
            order_data = database.child("userOrder").child(order_id).get().val()
            rate_data = database.child("ratings").child(rate_id).get().val()
            laundry_shop_data = database.child("laundry").child(reporter_id).get().val()

            riderId = order_data.get("riderId")
            rider_data = database.child("riders").child(riderId).get().val()
        
            pick_up_date_str = order_data.get("pickUpDate")
            try:
                pick_up_date = datetime.strptime(pick_up_date_str, "%m/%d/%Y")
                order_data["pickUpDate"] = pick_up_date.strftime("%d/%m/%Y")
            except ValueError:
                order_data["pickUpDate"] = "Invalid Date"
                
            order_status_data = database.child("orderStatus").child(order_id).get().val()
            if order_status_data:
                formatted_status_data = []
                for status_id, status_info in order_status_data.items():
                    status_datetime_str = status_info.get("dateTime")
                    try:
                        status_datetime = datetime.strptime(status_datetime_str, "%Y%m%d_%H%M%S")
                        
                        status_info["formatted_datetime"] = status_datetime.strftime("%Y/%m/%d %H:%M")
                    except ValueError:
                        status_info["formatted_datetime"] = "Invalid Date/Time"
                    formatted_status_data.append((status_id, status_info))

                # Sort the list of status items by date in reverse order
                sorted_order_status_data = sorted(formatted_status_data, key=lambda x: x[1]["formatted_datetime"], reverse=True)

            if reporter_data is not None and user_data is not None:
                context = {
                    'report_details_data': report_details_data,
                    'reporter_data': reporter_data,
                    'user_data': user_data,
                    'order_data': order_data,
                    'rate_data': rate_data,
                    'laundry_shop_data': laundry_shop_data,
                    'rider_data': rider_data,
                    'sorted_order_status_data':sorted_order_status_data
                }
                return render(request, 'reportsDetails.html', context)
        else:
            reporter_data = database.child("riders").child(reporter_id).get().val()
            user_data = database.child("users").child(user_id).get().val()
            order_data = database.child("userOrder").child(order_id).get().val()
            rate_data = database.child("ratings").child(rate_id).get().val()
            rider_data = database.child("riders").child(reporter_id).get().val()

            laundryId = order_data.get(laundryId)
            laundry_data = database.child("laundry").child(laundryId).get().val()
            
            pick_up_date_str = order_data.get("pickUpDate")
            try:
                pick_up_date = datetime.strptime(pick_up_date_str, "%m/%d/%Y")
                order_data["pickUpDate"] = pick_up_date.strftime("%d/%m/%Y")
            except ValueError:
                order_data["pickUpDate"] = "Invalid Date"

            order_status_data = database.child("orderStatus").child(order_id).get().val()
            if order_status_data:
                formatted_status_data = []
                for status_id, status_info in order_status_data.items():
                    status_datetime_str = status_info.get("dateTime")
                    try:
                        status_datetime = datetime.strptime(status_datetime_str, "%Y%m%d_%H%M%S")
                        
                        status_info["formatted_datetime"] = status_datetime.strftime("%Y/%m/%d %H:%M")
                    except ValueError:
                        status_info["formatted_datetime"] = "Invalid Date/Time"
                    formatted_status_data.append((status_id, status_info))

                # Sort the list of status items by date in reverse order
                sorted_order_status_data = sorted(formatted_status_data, key=lambda x: x[1]["formatted_datetime"], reverse=True)

            if reporter_data is not None and user_data is not None:
                context = {
                    'report_details_data': report_details_data,
                    'reporter_data': reporter_data,
                    'user_data': user_data,
                    'order_data': order_data,
                    'rate_data': rate_data,
                    'rider_data':rider_data,
                    'laundry_data':laundry_data,
                    'sorted_order_status_data':sorted_order_status_data
                }
                return render(request, 'reportsDetails.html', context)
    else:
        return render(request, 'reportsDetails.html')

@login_required
def allusersLaundryDetails(request, laundryId):
    laundry_data  = database.child("laundry").child(laundryId).get().val()
    if laundry_data is not None:
        context = {'laundry_data': laundry_data}
        return render(request, 'all-laundryDetails.html', context)
    else:
        return render(request, 'all-laundryDetails.html')

@login_required
def allusersUserDetails(request, userId):
    user_data  = database.child("users").child(userId).get().val()
    if user_data is not None:
        context = {'user_data': user_data}
        return render(request, 'all-userDetails.html', context)
    else:
        return render(request, 'all-userDetails.html')

@login_required
def allusersRiderDetails(request, riderId):
    rider_data  = database.child("riders").child(riderId).get().val()
    if rider_data is not None:
        context = {'rider_data': rider_data}
        return render(request, 'all-riderDetails.html', context)
    else:
        return render(request, 'all-riderDetails.html')

@login_required
def helpcentermessages(request):
    #get data from db
    help_data = database.child("helpCenter").get().val()
    #sort data
    sorted_help_data = sorted(help_data.items(), key=lambda x: x[1]['dateTime'], reverse=True)
    #pass
    return render(request, 'helpMessage.html', {"help_data": sorted_help_data})

@login_required
def helpdetails(request,helpId):
    help_data  = database.child("helpCenter").child(helpId).get().val()
    if help_data is not None:
        context = {'help_data': help_data}
        return render(request, 'helpDetails.html', context)
    else:
        return render(request, 'helpDetails.html')

@login_required
def manageallusers(request):
    user_data  = database.child("users").get().val()
    if user_data is not None:
        context = {'user_data': user_data}
        return render(request, 'all-users.html', context)
    else:
        return render(request, 'all-users.html')

@login_required
def managealllaundry(request):
    laundry_data  = database.child("laundry").get().val()
    if laundry_data is not None:
        context = {'laundry_data': laundry_data}
        return render(request, 'all-laundry.html', context)
    else:
        return render(request, 'all-laundry.html')

@login_required
def manageallriders(request):
    rider_data  = database.child("riders").get().val()
    if rider_data is not None:
        context = {'rider_data': rider_data}
        return render(request, 'all-riders.html', context)
    else:
        return render(request, 'all-riders.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')