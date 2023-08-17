from django.urls import include, path
from websiteapp import views
#URLConfig
urlpatterns = [
    path('', views.login, name="login"),
    path('newusers/', views.newusers, name="newusers"),
    path('ratingsreports/', views.ratingsreports, name="ratingsreports"),
    path('helpmessages/', views.helpcentermessages, name="helpmessages"),
    path('allusers/', views.manageallusers, name="allusers"),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('newlaundrydetails/', views.newlaundrydetails, name="newlaundrydetails"),
    path('newriderdetails/', views.newriderdetails, name="newriderdetails"),
    path('helpdetails/', views.helpdetails, name="helpdetails"),
    path('reportsdetails/', views.reportsdetails, name="reportsdetails"),
]