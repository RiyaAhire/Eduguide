from django.urls import path
from django.contrib.auth import views as auth_views
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
        "profile/",
        views.profile,
        name="profile"
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("saved-colleges/", views.saved_colleges, name="saved_colleges"),
    path("college/<int:college_id>/save/", views.toggle_saved_college, name="toggle_saved_college"),
    path("compare-shortlist/", views.compare_shortlist, name="compare_shortlist"),
    path("application-checklist/", views.application_checklist, name="application_checklist"),
    path("application-checklist/<int:task_id>/toggle/", views.toggle_checklist_task, name="toggle_checklist_task"),
    path("updates-reminders/", views.updates_reminders, name="updates_reminders"),
    path("reminders/<int:reminder_id>/toggle/", views.toggle_reminder, name="toggle_reminder"),
    path("reminders/<int:reminder_id>/delete/", views.delete_reminder, name="delete_reminder"),
    path("help/", views.help_faqs, name="help_faqs"),
    path("prediction/report/", views.prediction_report, name="prediction_report"),

    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
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
        "college/<str:college_code>/seat-matrix/",
        views.seat_matrix,
        name="seat_matrix",
    ),

    path(
        "courses/",
        views.courses,
        name="courses"
    ),

   path(
    "course-details/<int:course_id>/",
    views.course_details,
    name="course_details"
),

    path(
        "cutoff/",
        views.cutoff,
        name="cutoff"
    ),

    path(
        "cutoff/data/",
        views.cutoff_data,
        name="cutoff_data"
    ),
    path("cutoff/prediction/", views.cutoff_prediction_data, name="cutoff_prediction_data"),

    path(
        "prediction/",
        views.prediction,
        name="prediction"
    ),

    path(
        "prediction/data/",
        views.prediction_data,
        name="prediction_data"
    ),

    path(
        "prediction/report/pdf/",
        views.prediction_report_pdf,
        name="prediction_report_pdf"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

    path('admission-process/', 
         views.admission_process,
           name='admission_process'
    ),

]
