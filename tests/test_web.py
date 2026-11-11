from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from courses.models import Course
from employees.models import Employee
from enrollments.models import Enrollment


class BaseDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.python_course = Course.objects.create(
            title="Основы Python",
            category="Разработка",
            total_lessons=10,
        )
        cls.qa_course = Course.objects.create(
            title="Тестирование ПО",
            category="QA",
            total_lessons=20,
        )
        cls.ivanov = Employee.objects.create(
            full_name="Иванов Иван",
            department="Разработка",
        )
        cls.petrov = Employee.objects.create(
            full_name="Петров Пётр",
            department="QA",
        )


class CourseModelTests(BaseDataTestCase):
    def test_slug_is_generated_from_russian_title(self):
        assert self.python_course.slug == "osnovyi-python"
        assert self.qa_course.slug == "testirovanie-po"

    def test_get_absolute_url_uses_slug(self):
        url = self.python_course.get_absolute_url()
        assert url == f"/courses/{self.python_course.slug}/"
        assert reverse("courses:detail", kwargs={"slug": self.python_course.slug}) == url

    def test_generated_field_is_long(self):
        self.python_course.refresh_from_db()
        self.qa_course.refresh_from_db()
        assert self.python_course.is_long is False
        assert self.qa_course.is_long is True

    def test_generated_field_is_recalculated(self):
        self.python_course.total_lessons = 25
        self.python_course.save()
        self.python_course.refresh_from_db()
        assert self.python_course.is_long is True


class EnrollmentModelTests(BaseDataTestCase):
    def test_manager_methods_filter_by_status(self):
        active = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=10),
            total_questions=10,
        )
        cancelled = Enrollment.objects.create(
            employee=self.petrov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=10),
            total_questions=10,
        )
        cancelled.cancel()
        assert list(Enrollment.objects.active()) == [active]
        assert list(Enrollment.objects.cancelled()) == [cancelled]
        assert Enrollment.objects.active().count() == 1

    def test_record_progress_marks_completed(self):
        enrollment = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate(),
            total_questions=10,
        )
        enrollment.record_progress(lessons_completed=10, correct_answers=9)
        enrollment.refresh_from_db()
        assert enrollment.status == Enrollment.Status.COMPLETED
        assert enrollment.accuracy() == 90


class CourseViewTests(BaseDataTestCase):
    def test_detail_is_available_by_slug(self):
        response = self.client.get(self.python_course.get_absolute_url())
        assert response.status_code == 200
        assert "Основы Python" in response.content.decode()

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/courses/no-such-course/")
        assert response.status_code == 404

    def test_course_create_uploads_cover(self):
        # Минимальный корректный PNG 1x1
        image = SimpleUploadedFile(
            "cover.png",
            (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
                b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
                b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            ),
            content_type="image/png",
        )
        response = self.client.post(
            reverse("courses:create"),
            {
                "title": "Новый курс",
                "category": "Разработка",
                "total_lessons": 5,
                "cover": image,
            },
        )
        assert response.status_code == 302
        course = Course.objects.get(title="Новый курс")
        assert course.cover.name.startswith("courses/")

    def test_short_title_is_rejected(self):
        response = self.client.post(
            reverse("courses:create"),
            {"title": "AB", "category": "QA", "total_lessons": 5},
        )
        assert response.status_code == 200
        assert "не менее трёх символов" in response.content.decode()


class EnrollmentListTests(BaseDataTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.active = Enrollment.objects.create(
            employee=cls.ivanov,
            course=cls.python_course,
            deadline=timezone.localdate() + timedelta(days=5),
            total_questions=10,
        )
        cls.cancelled = Enrollment.objects.create(
            employee=cls.petrov,
            course=cls.qa_course,
            deadline=timezone.localdate() + timedelta(days=15),
            total_questions=10,
        )
        cls.cancelled.cancel()

    def test_status_filter_shows_only_active(self):
        response = self.client.get(reverse("enrollments:list"), {"status": "active"})
        objects = list(response.context["page_obj"].object_list)
        assert len(objects) == 1
        assert objects[0].employee.full_name == "Иванов Иван"

    def test_status_filter_shows_only_cancelled(self):
        response = self.client.get(reverse("enrollments:list"), {"status": "cancelled"})
        objects = list(response.context["page_obj"].object_list)
        assert len(objects) == 1
        assert objects[0].employee.full_name == "Петров Пётр"

    def test_invalid_date_is_reported_without_exception(self):
        response = self.client.get(
            reverse("enrollments:list"),
            {"deadline": "not-a-date"},
        )
        assert response.status_code == 200
        assert "deadline" in response.context["form"].errors

    def test_unknown_course_id_is_rejected_by_form(self):
        response = self.client.get(
            reverse("enrollments:list"),
            {"course": "9999"},
        )
        assert response.status_code == 200
        assert response.context["form"].errors

    def test_search_requires_two_characters(self):
        response = self.client.get(reverse("enrollments:list"), {"q": "И"})
        assert "не менее двух символов" in response.content.decode()

    def test_search_by_employee_name(self):
        response = self.client.get(reverse("enrollments:list"), {"q": "Петров"})
        assert response.context["page_obj"].paginator.count == 1

    def test_pagination(self):
        for number in range(6):
            Enrollment.objects.create(
                employee=self.ivanov,
                course=self.python_course,
                deadline=timezone.localdate() + timedelta(days=number + 1),
                total_questions=10,
            )
        response = self.client.get(reverse("enrollments:list"), {"page": 2})
        assert response.status_code == 200
        assert response.context["page_obj"].number == 2

    def test_context_processor_passes_counts(self):
        response = self.client.get(reverse("enrollments:list"))
        assert response.context["courses_count"] == 2
        assert response.context["employees_count"] == 2
        assert response.context["active_enrollments_count"] == 1


class EnrollmentFormTests(BaseDataTestCase):
    def _payload(self, **overrides):
        data = {
            "employee": self.ivanov.pk,
            "course": self.python_course.pk,
            "deadline": (timezone.localdate() + timedelta(days=7)).isoformat(),
            "total_questions": 10,
            "lessons_completed": 0,
            "correct_answers": 0,
        }
        data.update(overrides)
        return data

    def test_create_enrollment_redirects_and_saves(self):
        response = self.client.post(
            reverse("enrollments:create"),
            self._payload(),
        )
        enrollment = Enrollment.objects.get()
        assert response.status_code == 302
        assert response.url == reverse(
            "enrollments:detail",
            kwargs={"enrollment_id": enrollment.pk},
        )
        assert enrollment.status == Enrollment.Status.ACTIVE

    def test_past_deadline_is_rejected(self):
        response = self.client.post(
            reverse("enrollments:create"),
            self._payload(
                deadline=(timezone.localdate() - timedelta(days=1)).isoformat()
            ),
        )
        assert response.status_code == 200
        assert "прошедшую дату" in response.content.decode()
        assert Enrollment.objects.count() == 0

    def test_duplicate_active_enrollment_is_rejected(self):
        Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=3),
            total_questions=10,
        )
        response = self.client.post(
            reverse("enrollments:create"),
            self._payload(),
        )
        assert response.status_code == 200
        assert "уже есть активное назначение" in response.content.decode()
        assert Enrollment.objects.count() == 1

    def test_cancelled_enrollment_does_not_block_new_one(self):
        old = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=3),
            total_questions=10,
        )
        old.cancel()
        response = self.client.post(
            reverse("enrollments:create"),
            self._payload(),
        )
        assert response.status_code == 302
        assert Enrollment.objects.count() == 2

    def test_lessons_cannot_exceed_course_total(self):
        response = self.client.post(
            reverse("enrollments:create"),
            self._payload(lessons_completed=50),
        )
        assert response.status_code == 200
        assert "всего 10 уроков" in response.content.decode()

    def test_edit_does_not_conflict_with_itself(self):
        enrollment = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=3),
            total_questions=10,
        )
        response = self.client.post(
            reverse("enrollments:edit", kwargs={"enrollment_id": enrollment.pk}),
            self._payload(total_questions=20),
        )
        enrollment.refresh_from_db()
        assert response.status_code == 302
        assert enrollment.total_questions == 20

    def test_edit_rejects_conflict_with_other_enrollment(self):
        Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=3),
            total_questions=10,
        )
        other = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.qa_course,
            deadline=timezone.localdate() + timedelta(days=4),
            total_questions=10,
        )
        response = self.client.post(
            reverse("enrollments:edit", kwargs={"enrollment_id": other.pk}),
            self._payload(),
        )
        assert response.status_code == 200
        assert "уже есть активное назначение" in response.content.decode()

    def test_cancel_changes_status_and_keeps_record(self):
        enrollment = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=3),
            total_questions=10,
        )
        response = self.client.post(
            reverse("enrollments:cancel", kwargs={"enrollment_id": enrollment.pk})
        )
        enrollment.refresh_from_db()
        assert response.status_code == 302
        assert enrollment.status == Enrollment.Status.CANCELLED
        assert Enrollment.objects.count() == 1

    def test_cancel_requires_post(self):
        enrollment = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=3),
            total_questions=10,
        )
        response = self.client.get(
            reverse("enrollments:cancel", kwargs={"enrollment_id": enrollment.pk})
        )
        assert response.status_code == 405

    def test_missing_enrollment_returns_404(self):
        response = self.client.get(
            reverse("enrollments:detail", kwargs={"enrollment_id": 999})
        )
        assert response.status_code == 404


class StatisticsTests(BaseDataTestCase):
    def test_statistics_counts_statuses(self):
        active = Enrollment.objects.create(
            employee=self.ivanov,
            course=self.python_course,
            deadline=timezone.localdate() + timedelta(days=5),
            total_questions=10,
        )
        completed = Enrollment.objects.create(
            employee=self.petrov,
            course=self.qa_course,
            deadline=timezone.localdate() + timedelta(days=5),
            total_questions=10,
        )
        completed.record_progress(20, 18)
        response = self.client.get(reverse("enrollments:statistics"))
        assert response.context["active_count"] == 1
        assert response.context["completed_count"] == 1
        assert response.context["cancelled_count"] == 0
        assert active.pk not in [
            item["id"] for item in response.context["overdue"]
        ]


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password-123",
        )
        Course.objects.create(
            title="Тестовый курс",
            category="QA",
            total_lessons=5,
        )

    def test_admin_pages_for_domain_models(self):
        self.client.force_login(self.admin_user)
        for url in [
            "/admin/courses/course/",
            "/admin/employees/employee/",
            "/admin/enrollments/enrollment/",
            "/admin/courses/course/add/",
        ]:
            response = self.client.get(url)
            assert response.status_code == 200, url

    def test_course_admin_list_columns(self):
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/courses/course/")
        content = response.content.decode()
        assert "Активные назначения" in content
        assert "Длительный курс" in content
