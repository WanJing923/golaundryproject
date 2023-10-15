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
    
    #terminate and activate laundry shop
    path('terminate_laundry/<str:laundryId>/', views.terminate_laundry, name='terminate_laundry'),
    path('activate_laundry/<str:laundryId>/', views.activate_laundry, name='activate_laundry'),
    
    #reject and accept new laundry shop
    path('reject_laundry/<str:laundryId>/', views.reject_laundry, name='reject_laundry'),
    path('accept_laundry/<str:laundryId>/', views.accept_laundry, name='accept_laundry'),
    
    #terminate and activate rider
    path('terminate_rider/<str:riderId>/', views.terminate_rider, name='terminate_rider'),
    path('activate_rider/<str:riderId>/', views.activate_rider, name='activate_rider'),
    
    path('reject_rider/<str:riderId>/', views.reject_rider, name='reject_rider'),
    path('accept_rider/<str:riderId>/', views.accept_rider, name='accept_rider'),
    
    #terminate and activate user
    path('terminate_user/<str:userId>/', views.terminate_user, name='terminate_user'),
    path('activate_user/<str:userId>/', views.activate_user, name='activate_user'),
    
    #accept or reject ratings ratings
    path('reject_ratings/<str:reportId>/', views.reject_ratings, name='reject_ratings'),
    path('accept_ratings/<str:reportId>/', views.accept_ratings, name='accept_ratings'),
    
    
    
    
]