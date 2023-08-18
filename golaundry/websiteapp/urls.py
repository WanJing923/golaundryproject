from django.urls import include, path
from websiteapp import views
#URLConfig
urlpatterns = [
    # login and logout feature
    path('', views.login, name="login"),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # new laundry and rider feature
    path('newusers/', views.newusers, name="newusers"),
    path('newlaundrydetails/', views.newlaundrydetails, name="newlaundrydetails"),
    path('newriderdetails/', views.newriderdetails, name="newriderdetails"),
    
    # ratings report feature
    path('ratingsreports/', views.ratingsreports, name="ratingsreports"),
    path('reportsdetails/', views.reportsdetails, name="reportsdetails"),
    
    # help center message feature
    path('helpmessages/', views.helpcentermessages, name="helpmessages"),
    path('helpdetails/', views.helpdetails, name="helpdetails"),
    
    # manage all users feature
    path('allusers/', views.manageallusers, name="allusers"),
    path('alllaundry/', views.managealllaundry, name="alllaundry"),
    path('allriders/', views.manageallriders, name="allriders"),
    path('allusersUserDetails/', views.allusersUserDetails, name="allusersUserDetails"),
    path('allusersLaundryDetails/', views.allusersLaundryDetails, name="allusersLaundryDetails"),
    path('allusersRiderDetails/', views.allusersRiderDetails, name="allusersRiderDetails"),
]