from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from colleges.models import College, Course
from prediction.models import Cutoff, SeatMatrix
from users.models import Student


class PredictionDataTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("student", password="safe-password")
        Student.objects.create(
            user=self.user,
            full_name="Test Student",
            email="student@example.com",
            percentage=85,
            category="OPEN",
            branch="Computer Engineering",
            passing_year=2026,
            preferred_location="Any",
            college_type="Any",
            admission_year="2026-27",
        )
        college = College.objects.create(
            college_code="TEST01",
            college_name="Test Government Polytechnic",
            region="Pune",
            status="Government",
        )
        course = Course.objects.create(
            course_code="TEST01001",
            course_name="Computer Engineering",
            college=college,
        )
        Cutoff.objects.create(
            course=course,
            cap_round="CAP1",
            admission_year="2026-27",
            seat_category="General seats",
            category_code="NGOPENH",
            stage="Stage-I",
            cutoff_merit_no=100,
            cutoff_percentile=0.78,
        )
        Course.objects.create(
            course_code="TEST01002",
            course_name="Computer Science and Engineering",
            college=college,
        )

    def test_prediction_requires_login(self):
        response = self.client.post(reverse("prediction_data"))
        self.assertEqual(response.status_code, 302)

    def test_prediction_uses_saved_profile_and_cutoff_records(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("prediction_data"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["data_years"], ["2026-27"])
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["college"], "Test Government Polytechnic")
        self.assertEqual(payload["results"][0]["chance"], "Good chance")

    def test_prediction_returns_each_college_only_once(self):
        second_course = Course.objects.get(course_code="TEST01002")
        Cutoff.objects.create(
            course=second_course,
            cap_round="CAP1",
            admission_year="2026-27",
            seat_category="General seats",
            category_code="NGOPENH",
            stage="Stage-I",
            cutoff_merit_no=101,
            cutoff_percentile=0.76,
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("prediction_data"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)

    def test_prediction_matches_computer_technology_and_nashik_region(self):
        """Regression test for Government Polytechnic, Nashik at 96% OBC."""
        nashik = College.objects.create(
            college_code="NASHIK5010",
            college_name="Government Polytechnic, Nashik",
            region="Nashik",
            status="Government-Autonomous",
        )
        computer_technology = Course.objects.create(
            course_code="NASHIK501025110",
            course_name="Computer Technology",
            college=nashik,
        )
        Cutoff.objects.create(
            course=computer_technology,
            cap_round="CAP1",
            admission_year="2026-27",
            seat_category="Home District Non-Technical Seats",
            category_code="NGOBCH",
            stage="Stage-I",
            cutoff_merit_no=1025,
            cutoff_percentile=0.942,
        )
        self.user.student_profile.percentage = 96
        self.user.student_profile.category = "OBC"
        self.user.student_profile.preferred_location = "Nashik"
        self.user.student_profile.college_type = "Government"
        self.user.student_profile.save()
        self.client.force_login(self.user)

        response = self.client.post(reverse("prediction_data"))

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertTrue(any(result["college"] == "Government Polytechnic, Nashik" for result in results))

    def test_logged_in_student_can_update_personal_details(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("profile"), {
            "full_name": "Updated Student",
            "username": "updated-student",
            "email": "updated@example.com",
            "percentage": "91.5",
            "category": "OBC",
            "branch": "Information Technology",
            "passing_year": "2026",
            "preferred_location": "Pune",
            "college_type": "Government",
            "admission_year": "2026-27",
        })

        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.user.student_profile.refresh_from_db()
        self.assertEqual(self.user.username, "updated-student")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.student_profile.percentage, 91.5)

    def test_email_verification_link_marks_profile_verified(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.get(reverse("verify_email", args=[uid, token]))

        self.assertRedirects(response, reverse("login"))
        self.user.student_profile.refresh_from_db()
        self.assertTrue(self.user.student_profile.email_verified)

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)


class SeatMatrixViewTests(TestCase):
    def setUp(self):
        self.college = College.objects.create(
            college_code="SEAT01",
            college_name="Seat Matrix Polytechnic",
            region="Pune",
            status="Government",
        )
        self.course = Course.objects.create(
            course_code="SEAT01001",
            course_name="Computer Engineering",
            college=self.college,
        )

    def create_record(self, *, gender, category="OPEN"):
        return SeatMatrix.objects.create(
            course=self.course,
            admission_year="2026-27",
            cap_round="MATRIX",
            seat_type="Technical",
            district_type="HD",
            category=category,
            gender=gender,
            seat_count=1,
        )

    def test_seat_matrix_hides_invalid_values_and_uses_full_gender_labels(self):
        self.create_record(gender="G")
        self.create_record(gender="L", category="SC")
        self.create_record(gender="nan", category="OBC")

        response = self.client.get(reverse("seat_matrix", args=[self.college.college_code]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["gender_options"], [
            {"value": "Gents", "label": "Gents"},
            {"value": "Ladies", "label": "Ladies"},
        ])
        self.assertContains(response, "Gents")
        self.assertContains(response, "Ladies")
        self.assertNotContains(response, "nan", html=False)

    def test_seat_matrix_accepts_legacy_gender_filter_links(self):
        self.create_record(gender="G")
        self.create_record(gender="L", category="SC")

        response = self.client.get(
            reverse("seat_matrix", args=[self.college.college_code]),
            {"gender": "G"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_filters"]["gender"], "Gents")
        self.assertEqual([record.gender_label for record in response.context["page_obj"]], ["Gents"])
