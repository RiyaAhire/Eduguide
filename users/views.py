from colleges.models import College
from users.models import CourseInfo

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.models import User


def main_page(request):
    return render(
        request,
        "journal/index.html"
    )


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            return render(
                request,
                "journal/register.html",
                {
                    "error": "Passwords do not match."
                }
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "journal/register.html",
                {
                    "error": "Username already exists."
                }
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(
        request,
        "journal/register.html"
    )


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

            login(
                request,
                user
            )

            return redirect("index")

        return render(
            request,
            "journal/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "journal/login.html"
    )


def logout_view(request):

    if request.method == "POST":

        logout(request)

        return redirect("index")

    return redirect("index")


def colleges(request):

    colleges = College.objects.all().order_by(
        "college_name"
    )

    return render(
        request,
        "journal/colleges.html",
        {
            "colleges": colleges
        }
    )

def college_details(request, college_id):

    college = College.objects.get(id=college_id)

    return render(
        request,
        "journal/college_details.html",
        {
            "college": college
        }
    )


def course_details(request, course_id):

    course = CourseInfo.objects.get(id=course_id)
    course.subjects_list = course.major_subjects.split("|")
    course.skills_list = course.skills.split("|")
    course.career_list = course.career_opportunities.split("|")
    course.higher_studies_list = course.higher_studies.split("|")
    return render(
        request,
        "journal/course_details.html",
        {
            "course": course
        }
    )
def courses(request):

    courses = CourseInfo.objects.all().order_by("course_name")
    course_categories = (
        CourseInfo.objects
        .values_list("field", flat=True)
        .distinct()
        .order_by("field")
    )

    return render(
        request,
        "journal/courses.html",
        {
            "courses": courses,
            "course_categories": course_categories,
        }
    )




def cutoff(request):
    return render(
        request,
        "journal/cutoff.html"
    )


def prediction(request):
    return render(
        request,
        "journal/prediction.html"
    )


def about(request):
    return render(
        request,
        "journal/about.html"
    )
