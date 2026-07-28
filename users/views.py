from django.shortcuts import render

def main_page(request):
    return render(request, 'journal/index.html')

def home(request):
    return render(request,'journal/home.html')