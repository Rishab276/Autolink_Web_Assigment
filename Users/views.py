from django.shortcuts import render

def login_view(request):
    return render(request, 'Users/login.html')

def register_view(request):
    return render(request, 'Users/register.html')

def registerdetails_view(request):
    return render(request, 'Users/registerdetails.html')

def sellerRenterdetails_view(request):
    return render(request, 'Users/sellerRenterdetails.html')

def uploadvehicles_view(request):
    return render(request, 'Users/uploadvehicles.html')