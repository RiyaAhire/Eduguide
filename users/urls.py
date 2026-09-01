from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.main_page,
        name="index"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "colleges/",
        views.colleges,
        name="colleges"
    ),

    path(
        "college-details/<int:college_id>/",
        views.college_details,
        name="college_details"
    ),

    path(
        "courses/",
        views.courses,
        name="courses"
    ),

    path(
        "course-details/",
        views.course_details,
        name="course_details"
    ),

    path(
        "cutoff/",
        views.cutoff,
        name="cutoff"
    ),

    path(
        "prediction/",
        views.prediction,
        name="prediction"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

]