from django.shortcuts import render

def Main(request):
    return render(request, 'Main.html')

def index(request):
    return render(request, 'index.html')

def faq(request):
    return render(request, 'faq.html')

def aboutus_view(request):
    return render(request, 'aboutus.html')