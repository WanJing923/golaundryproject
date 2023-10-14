from django.urls import path
from websiteapp import views

#URLConfig
urlpatterns = [
    # login and logout feature
    path('', views.login_admin, name="login"),
    path('register', views.register, name="register"),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # new laundry and rider feature
    path('newusers/', views.newusers, name="newusers"),
    path('newlaundrydetails/<str:laundryId>/', views.newlaundrydetails, name="newlaundrydetails"),
    path('newriderdetails/<str:riderId>/', views.newriderdetails, name="newriderdetails"),
    
    # ratings report feature
    path('ratingsreports/', views.ratingsreports, name="ratingsreports"),
    path('reportsdetails/<str:reportId>/', views.reportsdetails, name="reportsdetails"),
    
    # help center message feature
    path('helpmessages/', views.helpcentermessages, name="helpmessages"),
    path('helpdetails/<str:helpId>/', views.helpdetails, name="helpdetails"),
    
    # manage all users feature
    path('allusers/', views.manageallusers, name="allusers"),
    path('alllaundry/', views.managealllaundry, name="alllaundry"),
    path('allriders/', views.manageallriders, name="allriders"),
    path('allusersUserDetails/<str:userId>/', views.allusersUserDetails, name="allusersUserDetails"),
    path('allusersLaundryDetails/<str:laundryId>/', views.allusersLaundryDetails, name="allusersLaundryDetails"),
    path('allusersRiderDetails/<str:riderId>/', views.allusersRiderDetails, name="allusersRiderDetails"),
    
    path('terminate_laundry/<str:laundryId>/', views.terminate_laundry, name='terminate_laundry'),
    path('activate_laundry/<str:laundryId>/', views.activate_laundry, name='activate_laundry'),
]