from django.shortcuts import render

# Create your views here.
def mainpage(request):
    return render(request, 'mainpage.html')

def login(request):
    return render(request, 'login.html')