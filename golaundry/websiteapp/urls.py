from django.urls import include, path
from websiteapp import views
#URLConfig
urlpatterns = [
    path('', views.login, name="login"),
]