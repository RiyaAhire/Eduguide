from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def main_page(request):
    return render(request, 'journal/index.html')



def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            return render(
                request,
                "users/register.html",
                {"error": "Passwords do not match."}
            )

        if User.objects.filter(username=username).exists():

            return render(
                request,
                "users/register.html",
                {"error": "Username already exists."}
            )

        User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

        return redirect("login")

    return render(request, "journal/register.html")

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("index")

        else:

            return render(
                request,
                "users/login.html",
                {"error": "Invalid username or password."}
            )

    return render(request, "journal/login.html")

def logout_view(request):

    if request.method == "POST":
        logout(request)
        return redirect("index")

    return redirect("home")

def colleges(request):
    return render(request, 'journal/colleges.html')

def college_details(request):
    return render(request, 'journal/college_details.html')

def courses(request):
    return render(request, 'journal/courses.html')

def course_details(request):
    return render(request, 'journal/course_details.html')

def cutoff(request):
    return render(request, 'journal/cutoff.html')

def prediction(request):
    return render(request, 'journal/prediction.html')

def about(request):
    return render(request, 'journal/about.html')