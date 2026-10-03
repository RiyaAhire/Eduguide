from colleges.models import College, Course
from users.models import CourseInfo, Student

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from prediction.models import Cutoff, SeatMatrix
from django.db import transaction
from django.db.models import Count, Max, Q
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from users.prediction_pdf import build_prediction_pdf


PROFILE_FIELDS = (
    "full_name", "username", "email", "percentage", "category", "branch",
    "preferred_location", "college_type", "admission_year", "passing_year",
)

FALLBACK_BRANCHES = (
    "Computer Engineering", "Information Technology", "Mechanical Engineering",
    "Civil Engineering", "Electrical Engineering", "Electronics & Telecommunication",
    "Aerospace Engineering", "Textile Engineering", "Dress Designing and Garment Manufacturing",
)


def prediction_branches(selected_branch=""):
    """Use the courses that actually have cutoff data, with useful first-run fallbacks."""
    branches = list(
        Course.objects.filter(cutoff__isnull=False)
        .values_list("course_name", flat=True)
        .distinct()
        .order_by("course_name")
    )
    if not branches:
        branches = list(FALLBACK_BRANCHES)
    if selected_branch and selected_branch not in branches:
        branches.append(selected_branch)
    return branches


def profile_context(form_data=None, **extra):
    context = {"form_data": form_data or {}}
    context["prediction_branches"] = prediction_branches(context["form_data"].get("branch", ""))
    context.update(extra)
    return context


def _profile_form_data(request):
    """Read and validate the fields shared by registration and profile editing."""
    data = {field: request.POST.get(field, "").strip() for field in PROFILE_FIELDS}
    if not all(data.values()):
        return data, "Please complete every required field."

    try:
        validate_email(data["email"])
        percentage = float(data["percentage"])
        passing_year = int(data["passing_year"])
    except (ValidationError, ValueError):
        return data, "Enter a valid email address, percentage and passing year."

    if not 0 <= percentage <= 100:
        return data, "Percentage must be between 0 and 100."
    if not 2000 <= passing_year <= 2100:
        return data, "Enter a valid passing year."

    data["percentage"] = percentage
    data["passing_year"] = passing_year
    return data, None


def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(reverse("verify_email", args=[uid, token]))
    send_mail(
        "Verify your EduGuide email address",
        "Welcome to EduGuide. Verify your email address by opening this link:\n\n" + verify_url,
        None,
        [user.email],
        fail_silently=True,
    )


def main_page(request):
    return render(
        request,
        "journal/index.html",
    )


def register(request):

    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form_data, error = _profile_form_data(request)
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if error or not password or not confirm_password:
            return render(
                request,
                "journal/register.html",
                profile_context(form_data, error=error or "Please complete every required field."),
            )

        if password != confirm_password:
            return render(
                request,
                "journal/register.html",
                profile_context(form_data, error="Passwords do not match."),
            )

        try:
            validate_password(password)
        except ValidationError as validation_error:
            return render(
                request,
                "journal/register.html",
                profile_context(form_data, error=" ".join(validation_error.messages)),
            )

        if User.objects.filter(username=form_data["username"]).exists():
            return render(
                request,
                "journal/register.html",
                profile_context(form_data, error="Username already exists."),
            )

        if User.objects.filter(email=form_data["email"]).exists() or Student.objects.filter(email=form_data["email"]).exists():
            return render(
                request,
                "journal/register.html",
                profile_context(form_data, error="An account with this email already exists."),
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=form_data["username"],
                email=form_data["email"],
                password=password,
            )
            Student.objects.create(
                user=user,
                full_name=form_data["full_name"],
                email=form_data["email"],
                percentage=form_data["percentage"],
                category=form_data["category"],
                branch=form_data["branch"],
                passing_year=form_data["passing_year"],
                preferred_location=form_data["preferred_location"],
                college_type=form_data["college_type"],
                admission_year=form_data["admission_year"],
            )
            transaction.on_commit(lambda: _send_verification_email(request, user))

        messages.success(request, "Account created. Check your email for the verification link.")
        return redirect("login")

    return render(request, "journal/register.html", profile_context())


def verify_email(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        Student.objects.filter(user=user).update(email_verified=True)
        messages.success(request, "Your email address has been verified. You can now sign in.")
    else:
        messages.error(request, "That verification link is invalid or has expired. Please request a new one.")
    return redirect("login")


@require_POST
def resend_verification(request):
    email = request.POST.get("email", "").strip()
    user = get_user_model().objects.filter(email__iexact=email).first()
    if user and hasattr(user, "student_profile") and not user.student_profile.email_verified:
        _send_verification_email(request, user)
    messages.success(request, "If that email belongs to an unverified account, a new verification link has been sent.")
    return redirect("login")


@login_required
def profile(request):
    """Allow a student to correct their account and prediction information."""
    student_profile = getattr(request.user, "student_profile", None)
    if student_profile is None:
        messages.error(request, "Your account does not have an admission profile yet. Please contact support.")
        return redirect("prediction")

    if request.method == "POST":
        form_data, error = _profile_form_data(request)
        if not error:
            username_exists = User.objects.exclude(pk=request.user.pk).filter(username=form_data["username"]).exists()
            email_exists = (
                User.objects.exclude(pk=request.user.pk).filter(email=form_data["email"]).exists()
                or Student.objects.exclude(pk=student_profile.pk).filter(email=form_data["email"]).exists()
            )
            if username_exists:
                error = "Username already exists."
            elif email_exists:
                error = "An account with this email already exists."

        if error:
            return render(request, "journal/profile.html", profile_context(form_data, error=error))

        with transaction.atomic():
            user = request.user
            email_changed = user.email.casefold() != form_data["email"].casefold()
            user.username = form_data["username"]
            user.email = form_data["email"]
            user.save(update_fields=["username", "email"])
            for field in PROFILE_FIELDS:
                if field != "username":
                    setattr(student_profile, field, form_data[field])
            if email_changed:
                student_profile.email_verified = False
            student_profile.save()
            if email_changed:
                transaction.on_commit(lambda: _send_verification_email(request, user))

        messages.success(request, "Your personal details have been updated." if not email_changed else "Your details were updated. Please verify your new email address.")
        return redirect("profile")

    form_data = {
        "full_name": student_profile.full_name,
        "username": request.user.username,
        "email": request.user.email,
        "percentage": student_profile.percentage,
        "category": student_profile.category,
        "branch": student_profile.branch,
        "passing_year": student_profile.passing_year,
        "preferred_location": student_profile.preferred_location,
        "college_type": student_profile.college_type,
        "admission_year": student_profile.admission_year,
    }
    return render(request, "journal/profile.html", profile_context(form_data))


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

            # Take the student straight back to the feature that uses the
            # account-linked profile.  The prediction page loads the saved
            # Student record for this authenticated user.
            return redirect("prediction")

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

    college = get_object_or_404(College, id=college_id)

    return render(
        request,
        "journal/college_details.html",
        {
            "college": college
        }
    )


def seat_matrix(request, college_code):
    """Explore one college's seat records with database filtering and pagination."""
    college = get_object_or_404(College, college_code=college_code)
    base_records = SeatMatrix.objects.filter(
        course__college=college
    ).select_related("course", "course__college")

    filter_fields = {
        "course": "course_id",
        "admission_year": "admission_year",
        "seat_type": "seat_type",
        "district_type": "district_type",
        "category": "category",
        "gender": "gender",
    }
    selected = {key: request.GET.get(key, "").strip() for key in filter_fields}
    records = base_records
    for key, field in filter_fields.items():
        value = selected[key]
        if value:
            records = records.filter(**{field: value})

    options = {}
    for key, field in filter_fields.items():
        options[key] = base_records.values_list(field, flat=True).distinct().order_by(field)

    available_courses = Course.objects.filter(
        seatmatrix__course__college=college
    ).distinct().order_by("course_name")

    paginator = Paginator(records.order_by("course__course_name", "admission_year", "seat_type", "category"), 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "college": college,
        "filter_options": options,
        "available_courses": available_courses,
        "selected_filters": selected,
        "page_obj": page_obj,
        "number_of_courses": college.courses.count(),
        "total_seat_records": base_records.count(),
        "legend": [
            ("G", "General"), ("L", "Ladies"), ("HD", "Home District"),
            ("OHD", "Other Home District"), ("OPEN", "Open Category"),
            ("SC", "Scheduled Caste"), ("ST", "Scheduled Tribe"),
            ("VJDT", "Vimukta Jati / Denotified Tribes"), ("NTB", "Nomadic Tribe B"),
            ("NTC", "Nomadic Tribe C"), ("NTD", "Nomadic Tribe D"),
            ("OBC", "Other Backward Class"),
            ("SEBC", "Socially and Educationally Backward Class"),
            ("ORPHAN", "Orphan Reservation"), ("PWD", "Persons with Disabilities"),
            ("DEF", "Defence Category"), ("NA", "Not Applicable"),
        ],
    }
    return render(request, "journal/seat_matrix.html", context)


def course_details(request, course_id):

    course = get_object_or_404(CourseInfo, id=course_id)
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
    admission_years = (
        Cutoff.objects
        .values_list("admission_year", flat=True)
        .distinct()
        .order_by("-admission_year")
    )

    return render(
        request,
        "journal/cutoff.html",
        {"admission_years": admission_years},
    )


@require_GET
def cutoff_data(request):
    """Return valid cutoff filters and matching records for the selected course."""
    year = request.GET.get("year", "")
    college_id = request.GET.get("college", "")
    course_id = request.GET.get("course", "")
    category = request.GET.get("category", "")
    cap_round = request.GET.get("round", "")

    cutoffs = Cutoff.objects.select_related("course__college")
    if year:
        cutoffs = cutoffs.filter(admission_year=year)

    colleges = list(
        cutoffs.values(
            "course__college_id", "course__college__college_name"
        ).distinct().order_by("course__college__college_name")
    )

    if college_id.isdigit():
        cutoffs = cutoffs.filter(course__college_id=college_id)
    else:
        college_id = ""

    courses = list(
        cutoffs.values("course_id", "course__course_name")
        .distinct().order_by("course__course_name")
    )

    if course_id.isdigit():
        cutoffs = cutoffs.filter(course_id=course_id)
    else:
        course_id = ""

    categories = list(
        cutoffs.values_list("category_code", flat=True)
        .distinct().order_by("category_code")
    )
    # The admission process has four CAP rounds. Keep all four available
    # even when a particular course has no record in one of those rounds.
    rounds = ["CAP1", "CAP2", "CAP3", "CAP4"]

    records = []
    if course_id:
        if category:
            cutoffs = cutoffs.filter(category_code=category)
        if cap_round:
            cutoffs = cutoffs.filter(cap_round=cap_round)

        records = [
            {
                "category": cutoff.category_code,
                "seat_category": cutoff.seat_category,
                "round": cutoff.cap_round,
                "percentile": round(cutoff.cutoff_percentile * 100, 2),
                "merit_no": cutoff.cutoff_merit_no,
                "stage": cutoff.stage,
            }
            for cutoff in cutoffs.order_by(
                "category_code", "cap_round", "seat_category", "stage"
            )
        ]

    return JsonResponse({
        "colleges": [
            {"id": item["course__college_id"], "name": item["course__college__college_name"]}
            for item in colleges
        ],
        "courses": [
            {"id": item["course_id"], "name": item["course__course_name"]}
            for item in courses
        ],
        "categories": categories,
        "rounds": rounds,
        "records": records,
    })


def prediction(request):
    student_profile = None
    if request.user.is_authenticated:
        student_profile = getattr(request.user, "student_profile", None)

    return render(
        request,
        "journal/prediction.html",
        {"student_profile": student_profile},
    )


def _branch_terms(branch):
    """Return practical database search terms for a saved branch preference."""
    aliases = {
        "Electronics & Telecommunication": [
            "electronics and telecommunication",
            "electronics and communication",
            "electronics engineering",
        ],
        "Information Technology": ["information technology"],
        "Computer Engineering": [
            "computer engineering",
            "computer science",
            "computer technology",
        ],
        "Aerospace Engineering": ["aerospace engineering", "aeronautical engineering"],
    }
    return aliases.get(branch, [branch])


def _prediction_years(available_years):
    """Use both of the two latest historical years when they are available."""
    return available_years[:2]


def _college_type_filter(college_type):
    """Map student-friendly college types to the terminology in source data."""
    filters = {
        "Government": Q(course__college__status__icontains="government"),
        "Private": (
            Q(course__college__status__icontains="private")
            | Q(course__college__status__icontains="un-aided")
            | Q(course__college__status__icontains="unaided")
        ),
        "Autonomous": Q(course__college__status__icontains="autonomous"),
    }
    return filters.get(college_type, Q())


def _chance_for_margin(margin):
    """Classify a score gap from historical cutoff data in percentage points."""
    if margin >= 8:
        return "High chance", "high", min(96, round(76 + margin * 2))
    if margin >= 3:
        return "Good chance", "good", min(75, round(58 + margin * 2))
    if margin >= -3:
        return "Moderate chance", "moderate", round(48 + margin * 2)
    return "Stretch chance", "stretch", max(15, round(40 + margin * 2))


@require_POST
@login_required
def prediction_data(request):
    """Build admission recommendations from the signed-in student's saved profile."""
    profile = getattr(request.user, "student_profile", None)
    if profile is None:
        return JsonResponse(
            {"error": "Complete an admission profile before using prediction."},
            status=403,
        )

    branch_filter = Q()
    for term in _branch_terms(profile.branch):
        branch_filter |= Q(course__course_name__icontains=term)

    cutoffs = Cutoff.objects.select_related("course__college").filter(branch_filter)
    available_years = list(
        cutoffs.values_list("admission_year", flat=True).distinct().order_by("-admission_year")
    )
    if not available_years:
        return JsonResponse({"results": [], "error": "No cutoff records are available for your preferred branch."})

    data_years = _prediction_years(available_years)
    cutoffs = cutoffs.filter(admission_year__in=data_years)

    # Codes such as NGOBC and NGSCH contain the student's reservation category.
    # Exclude seats that require extra eligibility information we do not collect.
    cutoffs = cutoffs.filter(category_code__icontains=profile.category).exclude(
        Q(category_code__icontains="PWD")
        | Q(category_code__icontains="DEF")
        | Q(category_code__icontains="ORPHAN")
        | Q(category_code__icontains="TFWS")
    )

    if profile.preferred_location and profile.preferred_location != "Any":
        cutoffs = cutoffs.filter(course__college__region__iexact=profile.preferred_location)

    if profile.college_type and profile.college_type != "Any":
        cutoffs = cutoffs.filter(_college_type_filter(profile.college_type))

    grouped = (
        cutoffs.values(
            "course__college_id",
            "course__course_name",
            "course__college__college_name",
            "course__college__region",
            "course__college__status",
            "course__college__college_code",
            "course__college__website_info__website",
        )
        .annotate(
            # Use the most competitive applicable cutoff across the two latest
            # historical years. This is safer than averaging separate CAP
            # rounds, stages and seat categories into a fictional threshold.
            reference_cutoff=Max("cutoff_percentile"),
            records_used=Count("id"),
        )
    )

    # More than one branch/course can match at a college. Keep its strongest
    # matching course so a student never receives duplicate college cards.
    results_by_college = {}
    for item in grouped:
        cutoff_percent = item["reference_cutoff"] * 100
        margin = profile.percentage - cutoff_percent
        # Recommendations more than 8 percentage points below the student's
        # score are too unlikely to present as a useful college prediction.
        if margin < -8:
            continue

        label, level, confidence = _chance_for_margin(margin)
        result = {
            "college_id": item["course__college_id"],
            "college": item["course__college__college_name"],
            "course": item["course__course_name"],
            "location": item["course__college__region"] or "Location not listed",
            "college_type": item["course__college__status"] or "College type not listed",
            "college_code": item["course__college__college_code"],
            "official_website": item["course__college__website_info__website"] or "",
            "chance": label,
            "level": level,
            "confidence": confidence,
            "cutoff": round(cutoff_percent, 2),
            "cutoff_basis": "Most competitive eligible cutoff across two years",
            "margin": round(margin, 2),
            "records_used": item["records_used"],
        }
        college_key = (
            (item["course__college__college_name"] or "").casefold().strip(),
            (item["course__college__region"] or "").casefold().strip(),
        )
        existing = results_by_college.get(college_key)
        if existing is None or (result["confidence"], result["margin"], result["records_used"], result["course"]) > (
            existing["confidence"], existing["margin"], existing["records_used"], existing["course"]
        ):
            results_by_college[college_key] = result

    results = list(results_by_college.values())
    results.sort(key=lambda result: (result["confidence"], result["margin"]), reverse=True)
    report_data = {
        "results": results[:24],
        "data_years": data_years,
        "requested_year": profile.admission_year,
        "used_latest_year": profile.admission_year not in data_years,
        "profile": {
            "percentage": profile.percentage,
            "category": profile.category,
            "branch": profile.branch,
        },
    }
    request.session["latest_prediction_report"] = {
        **report_data,
        "profile": {
            "name": profile.full_name or request.user.get_full_name() or request.user.username,
            "percentage": profile.percentage,
            "category": profile.category,
            "branch": profile.branch,
            "location": profile.preferred_location or "Any",
            "college_type": profile.college_type or "Any",
            "admission_year": profile.admission_year,
        },
    }
    return JsonResponse(report_data)


@require_POST
@login_required
def prediction_report_pdf(request):
    """Download a standalone prediction PDF without browser print furniture."""
    report = request.session.get("latest_prediction_report")
    if not report:
        return JsonResponse(
            {"error": "Calculate your college matches before downloading the report."},
            status=409,
        )
    pdf = build_prediction_pdf(report)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="EduGuide-Prediction-Report.pdf"'
    response["Cache-Control"] = "no-store"
    return response


def admission_process(request):
    return render(request, 'journal/admission_process.html')


def about(request):
    return render(
        request,
        "journal/about.html"
    )
