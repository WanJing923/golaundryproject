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
import firebase_admin
from firebase_admin import auth
import os
from django.conf import settings
from django.core.mail import send_mail

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
authFirebase = firebase.auth()
database=firebase.database()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
keyfile_path = os.path.join(BASE_DIR, 'keyfile.json')

cred = firebase_admin.credentials.Certificate(keyfile_path)
firebase_admin.initialize_app(cred)

########################################

def register(request):
    if request.method == 'POST':
        email_address = request.POST.get('email_address')
        password = request.POST.get('password')

        try:
            user = authFirebase.create_user_with_email_and_password(email_address, password) 
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
            firebase_user_id = authFirebase.sign_in_with_email_and_password(email_address, password)['localId']

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
    
    sorted_laundry_data = []
    sorted_rider_data = []

    for laundry_id, laundry_info in laundry_data.items():
        if laundry_info.get("isNew") == True:
            sorted_laundry_data.append((laundry_id, laundry_info))

    for rider_id, rider_info in rider_data.items():
        if rider_info.get("isNew") == True:
            sorted_rider_data.append((rider_id, rider_info))
            
    #sort data
    sorted_laundry_data = sorted(sorted_laundry_data, key=lambda x: x[1]['registerDateTime'], reverse=True)
    sorted_rider_data = sorted(sorted_rider_data, key=lambda x: x[1]['registerDateTime'], reverse=True)
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

    if reports_data:
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
    else:
        return render(request, 'reports.html')
        
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
            rate_data = database.child("ratingsLaundry").child(rate_id).get().val()
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

            if reporter_data is not None:
                context = {
                    'report_details_data': report_details_data,
                    'reporter_data': reporter_data,
                    'user_data': user_data,
                    'order_data': order_data,
                    'rate_data': rate_data,
                    'laundry_shop_data': laundry_shop_data,
                    'rider_data': rider_data,
                    'sorted_order_status_data': sorted_order_status_data
                }
                return render(request, 'reportsDetails.html', context)
        else:
            reporter_data = database.child("riders").child(reporter_id).get().val()
            user_data = database.child("users").child(user_id).get().val()
            order_data = database.child("userOrder").child(order_id).get().val()
            rate_data = database.child("ratingsRider").child(rate_id).get().val()
            rider_data = database.child("riders").child(reporter_id).get().val()

            laundryId = order_data.get("laundryId")
            laundry_shop_data = database.child("laundry").child(laundryId).get().val()
            
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

            if reporter_data is not None:
                context = {
                    'report_details_data': report_details_data,
                    'reporter_data': reporter_data,
                    'user_data': user_data,
                    'order_data': order_data,
                    'rate_data': rate_data,
                    'rider_data': rider_data,
                    'laundry_shop_data':laundry_shop_data,
                    'sorted_order_status_data': sorted_order_status_data
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
        # Sort user_data by fullName
        sorted_user_data = sorted(user_data.items(), key=lambda item: item[1]['fullName'].lower())
        
        context = {'user_data': sorted_user_data}
        return render(request, 'all-users.html', context)
    else:
        return render(request, 'all-users.html')

@login_required
def managealllaundry(request):
    laundry_data  = database.child("laundry").get().val()
    if laundry_data is not None:
        sorted_laundry_data = []
        
        for laundry_id, laundry_info in laundry_data.items():
            if laundry_info.get("isNew") == False:
                sorted_laundry_data.append((laundry_id, laundry_info))
            
        sorted_laundry_data = sorted(sorted_laundry_data, key=lambda item: item[1]['shopName'].lower())
        
        context = {'laundry_data': sorted_laundry_data}
        return render(request, 'all-laundry.html', context)
    else:
        return render(request, 'all-laundry.html')

@login_required
def manageallriders(request):
    rider_data  = database.child("riders").get().val()
    if rider_data is not None:
        sorted_rider_data = []
        
        for rider_id, rider_info in rider_data.items():
            if rider_info.get("isNew") == False:
                sorted_rider_data.append((rider_id, rider_info))
                
        sorted_rider_data = sorted(sorted_rider_data, key=lambda item: item[1]['fullName'].lower())
        
        context = {'rider_data': sorted_rider_data}
        return render(request, 'all-riders.html', context)
    else:
        return render(request, 'all-riders.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    
##########################################################

# terminate/activate laundry shop
def terminate_laundry(request, laundryId):
    try:
        laundry_data = database.child("laundry").child(laundryId).get().val()
        
        if laundry_data:
            laundry_data["status"] = "terminated"
            database.child("laundry").child(laundryId).update({"status": "terminated"})
            
            # send email to inform
            subject = 'Go-Laundry: Your account has been terminated'
            message = f'Dear owner of {laundry_data["shopName"]}, \n\nWe would like to inform you about your account has been terminated.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [laundry_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'Laundry shop "{laundry_data["shopName"]}" has been terminated. An email has been sent.')
        else:
            messages.error(request, 'Laundry shop not found.')
    except Exception as e:
        messages.error(request, f'Error terminating laundry shop: {str(e)}')
    return redirect('alllaundry') 

def activate_laundry(request, laundryId):
    try:
        laundry_data = database.child("laundry").child(laundryId).get().val()

        if laundry_data:
            laundry_data["status"] = "active"
            database.child("laundry").child(laundryId).update({"status": "active"})
            
            # send email to inform
            subject = 'Go-Laundry: Your account has been activated'
            message = f'Dear owner of {laundry_data["shopName"]}, \n\nWe would like to inform you about your account has been activated.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [laundry_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'Laundry shop "{laundry_data["shopName"]}" has been activated. An email has been sent.')
        else:
            messages.error(request, 'Laundry shop not found.')
    except Exception as e:
        messages.error(request, f'Error activating laundry shop: {str(e)}')
    return redirect('alllaundry')

# reject or accept new laundry shop
def reject_laundry(request, laundryId):
    try:
        laundry_data = database.child("laundry").child(laundryId).get().val()

        if laundry_data:
            # send email to inform
            subject = 'Go-Laundry: Your new account has been rejected'
            message = f'Dear owner of {laundry_data["shopName"]}, \n\nWe would like to inform you about your new account has been rejected and removed by the admin due to insufficient or invalid information.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [laundry_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            database.child("laundry").child(laundryId).remove()

            user_uid = laundry_data.get("uid")
            if user_uid:
                delete_firebase_user_by_uid(user_uid)

            messages.success(request, f'Laundry shop "{laundry_data["shopName"]}" has been removed. An email has been sent.')
        else:
            messages.error(request, 'Laundry shop not found.')
    except Exception as e:
        messages.error(request, f'Error removing laundry shop: {str(e)}')
    return redirect('newusers')

def delete_firebase_user_by_uid(uid):
    try:
        auth.delete_user(uid)
    except auth.AuthError as e:
        print(f"Error deleting Firebase user: {e}")
        
def accept_laundry(request, laundryId):
    try:
        laundry_data = database.child("laundry").child(laundryId).get().val()

        if laundry_data:
            # send email to inform
            subject = 'Go-Laundry: Your new account has been activated'
            message = f'Dear owner of {laundry_data["shopName"]}, \n\nWe would like to inform you about your new account has been activated by the admin. You can login into account and setup your shop now! Please be noted that you must provide full shop information and services information to complete the shop setup.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [laundry_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            laundry_data["status"] = "active"
            database.child("laundry").child(laundryId).update({"status": "active"})
            
            laundry_data["isNew"] = False
            database.child("laundry").child(laundryId).update({"isNew": False})
            
            messages.success(request, f'Laundry shop "{laundry_data["shopName"]}" has been accepted. An email has been sent.')
        else:
            messages.error(request, 'Laundry shop not found.')
    except Exception as e:
        messages.error(request, f'Error accepting laundry shop: {str(e)}')
    return redirect('newusers')

################################################

# terminate/activate rider
def terminate_rider(request, riderId):
    try:
        rider_data = database.child("riders").child(riderId).get().val()
        
        if rider_data:
            
            rider_data["status"] = "terminated"
            database.child("riders").child(riderId).update({"status": "terminated"})
            
            # send email to inform
            subject = 'Go-Laundry: Your account has been terminated'
            message = f'Dear {rider_data["fullName"]}, \n\nWe would like to inform you about your account has been terminated.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [rider_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'Rider "{rider_data["fullName"]}" has been terminated. An email has been sent.')
        else:
            messages.error(request, 'Rider not found.')
    except Exception as e:
        messages.error(request, f'Error terminating rider: {str(e)}')
    return redirect('allriders') 

def activate_rider(request, riderId):
    try:
        rider_data = database.child("riders").child(riderId).get().val()

        if rider_data:
            rider_data["status"] = "active"
            database.child("riders").child(riderId).update({"status": "active"})
            
            # send email to inform
            subject = 'Go-Laundry: Your account has been activated'
            message = f'Dear {rider_data["fullName"]}, \n\nWe would like to inform you about your account has been activated.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [rider_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'Rider "{rider_data["fullName"]}" has been activated. An email has been sent.')
        else:
            messages.error(request, 'Rider not found.')
    except Exception as e:
        messages.error(request, f'Error activating rider: {str(e)}')
    return redirect('allriders')

def reject_rider(request, riderId):
    try:
        rider_data = database.child("riders").child(riderId).get().val()

        if rider_data:
            # send email to inform
            subject = 'Go-Laundry: Your new account has been rejected'
            message = f'Dear {rider_data["fullName"]}, \n\nWe would like to inform you about your new account has been rejected and removed by the admin due to insufficient or invalid information.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [rider_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            database.child("riders").child(riderId).remove()

            user_uid = rider_data.get("uid")
            if user_uid:
                delete_firebase_user_by_uid(user_uid)

            messages.success(request, f'Rider "{rider_data["fullName"]}" has been removed. An email has been sent.')
        else:
            messages.error(request, 'Rider not found.')
    except Exception as e:
        messages.error(request, f'Error removing rider: {str(e)}')
    return redirect('newusers')
        
def accept_rider(request, riderId):
    try:
        rider_data = database.child("riders").child(riderId).get().val()

        if rider_data:
            rider_data["status"] = "active"
            database.child("riders").child(riderId).update({"status": "active"})
            
            rider_data["isNew"] = False
            database.child("riders").child(riderId).update({"isNew": False})
            
            # send email to inform
            subject = 'Go-Laundry: Your new account has been activated'
            message = f'Dear {rider_data["fullName"]}, \n\nWe would like to inform you about your new account has been activated by the admin. You can login into account and find available order within the working hours now!\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [rider_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'Rider "{rider_data["fullName"]}" has been accepted. An email has been sent.')
        else:
            messages.error(request, 'Rider not found.')
    except Exception as e:
        messages.error(request, f'Error accepting rider: {str(e)}')
    return redirect('newusers')

###############################################

# terminate/activate user
def terminate_user(request, userId):
    try:
        user_data = database.child("users").child(userId).get().val()
        
        if user_data:
            user_data["status"] = "terminated"
            database.child("users").child(userId).update({"status": "terminated"})
            
            # send email to inform
            subject = 'Go-Laundry: Your account has been terminated'
            message = f'Dear {user_data["fullName"]}, \n\nWe would like to inform you about your account "{user_data["fullName"]}" has been terminated.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'User "{user_data["fullName"]}" has been terminated. An email has been sent.')
        else:
            messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'Error terminating user: {str(e)}')
    return redirect('allusers') 

def activate_user(request, userId):
    try:
        user_data = database.child("users").child(userId).get().val()

        if user_data:
            user_data["status"] = "active"
            database.child("users").child(userId).update({"status": "active"})
            
            # send email to inform
            subject = 'Go-Laundry: Your account has been activated'
            message = f'Dear {user_data["fullName"]}, \n\nWe would like to inform you about your account "{user_data["fullName"]}" has been activated. Welcome to Go-Laundry application.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
            
            messages.success(request, f'User "{user_data["fullName"]}" has been activated. An email has been sent.')
        else:
            messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'Error activating user: {str(e)}')
    return redirect('allusers')

############################################

def reject_ratings(request, reportId):
    try:
        report_data = database.child("reports").child(reportId).get().val()
        
        if report_data:
            reporter_role = report_data.get("reporterRole")
            reporter_id = report_data.get("reporterId")
            rate_id = report_data.get("rateId")
            
            if reporter_role == "laundry":
                
                laundry_data = database.child("laundry").child(reporter_id).get().val()
                laundry_email = laundry_data.get("emailAddress")
                laundry_shopName = laundry_data.get("shopName")
                
                # send email to inform
                subject = 'Go-Laundry: The ratings has been removed'
                message = f'Dear owner of {laundry_shopName}, \n\nWe would like to inform you about your ratings report has been reviewed by the admin and the review from customer has been removed.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = laundry_email
                send_mail( subject, message, email_from, recipient_list )
                    
                database.child("ratingsLaundry").child(rate_id).remove()
                # calculate average and set value again
                current_ratings_laundry = database.child("ratingsLaundry").get().val()
                if current_ratings_laundry is not None:
                    laundry_ratings_data_final = []
                    for laundry_ratings_data_id, ratings_data in current_ratings_laundry.items():
                        if ratings_data.get("laundryId") == reporter_id:
                            laundry_ratings_data_final.append(ratings_data)
                            
                    total_rate = 0
                    num_ratings = 0
                    for data in laundry_ratings_data_final:
                        total_rate += data.get("rateToLaundry")
                        num_ratings += 1
                    if num_ratings > 0:
                        average_rate = total_rate / num_ratings
                    else:
                        average_rate = 0
                        
                    database.child("laundry").child(reporter_id).update({"ratingsAverage": average_rate})
                    database.child("reports").child(reportId).remove()

                    messages.success(request, f'Ratings from customer "{rate_id}" have been removed. An email has been sent.')
                    messages.success(request, f'New ratings average for the laundry shop: {average_rate}')
                    
            else: #rider
                
                rider_data = database.child("riders").child(reporter_id).get().val()
                rider_email = rider_data.get("emailAddress")
                rider_fullName = rider_data.get("fullName")
                    
                # send email to inform
                subject = 'Go-Laundry: The ratings has been removed'
                message = f'Dear {rider_fullName}, \n\nWe would like to inform you about your ratings report has been reviewed by the admin and the review from customer has been removed.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = rider_email
                send_mail( subject, message, email_from, recipient_list )
                    
                database.child("ratingsRider").child(rate_id).remove()
                # calculate average and set value again
                current_ratings_rider = database.child("ratingsRider").get().val()
                if current_ratings_rider is not None:
                    rider_ratings_data_final = []
                    for rider_ratings_data_id, ratings_data in current_ratings_rider.items():
                        if ratings_data.get("riderId") == reporter_id:
                            rider_ratings_data_final.append(ratings_data)
                            
                    total_rate = 0
                    num_ratings = 0
                    for data in rider_ratings_data_final:
                        total_rate += data.get("rateToRider")
                        num_ratings += 1
                    if num_ratings > 0:
                        average_rate = total_rate / num_ratings
                    else:
                        average_rate = 0
                        
                    database.child("riders").child(reporter_id).update({"ratingsAverage": average_rate})
                    database.child("reports").child(reportId).remove()

                    messages.success(request, f'Ratings from customer "{rate_id}" have been removed. An email has been sent.')
                    messages.success(request, f'New ratings average for the rider: {average_rate}')
                    
        else:
            messages.error(request, 'Ratings report not found.')
    except Exception as e:
        messages.error(request, f'Error removing ratings: {str(e)}')
    return redirect('ratingsreports')

def accept_ratings(request, reportId):
    try:
        database.child("reports").child(reportId).update({"adminResponse": True})
        report_data = database.child("reports").child(reportId).get().val()
        
        if report_data:
            reporter_role = report_data.get("reporterRole")
            reporter_id = report_data.get("reporterId")
            
            if reporter_role == "laundry":
        
                laundry_data = database.child("laundry").child(reporter_id).get().val()
                laundry_email = laundry_data.get("emailAddress")
                laundry_shopName = laundry_data.get("shopName")
                    
                # send email to inform
                subject = 'Go-Laundry: The ratings report has been rejected'
                message = f'Dear owner of {laundry_shopName}, \n\nWe would like to inform you about your ratings report has been reviewed by the admin and the review from customer has been accepted.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = laundry_email
                send_mail( subject, message, email_from, recipient_list )
            
            else:
                rider_data = database.child("riders").child(reporter_id).get().val()
                rider_email = rider_data.get("emailAddress")
                rider_fullName = rider_data.get("fullName")
                    
                # send email to inform
                subject = 'Go-Laundry: The ratings report has been rejected'
                message = f'Dear {rider_fullName}, \n\nWe would like to inform you about your ratings report has been reviewed by the admin and the review from customer has been accepted.\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = rider_email
                send_mail( subject, message, email_from, recipient_list )
                    
        messages.error(request, 'Ratings accepted. An email has been sent.')
    except Exception as e:
        messages.error(request, f'Error accepting ratings: {str(e)}')
    return redirect('ratingsreports')

#############################################

#reply help center message
def reply_help(request, helpId):
    help_data  = database.child("helpCenter").child(helpId).get().val()
    context = {'help_data': help_data}

    if request.method == 'POST':
        reply_message = request.POST.get('reply_message')
        
        if not reply_message:
            messages.error(request, 'Reply message cannot be empty.')
        else:
            help_data = database.child("helpCenter").child(helpId).get().val()
            
            help_data["status"] = "Solved"
            database.child("helpCenter").child(helpId).update({"status": "Solved"})
            
            # send email to inform
            subject = 'Go-Laundry: Replying from Help Center'
            message = f'Dear user, \n\nFor the {help_data["title"]} problem, our admin has made response as below:\n\n"{reply_message}"\n\nPlease contact us via help center or replying this email if you have any concern.\n\n\nRegards:\nGo-Laundry Official'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [help_data["emailAddress"]]
            send_mail( subject, message, email_from, recipient_list )
        
            messages.success(request, 'Reply message sent through email successfully.')
            return redirect('helpmessages')
        
    return render(request, 'helpDetails.html', context)


















