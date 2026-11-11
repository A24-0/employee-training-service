from django import forms
from django.utils import timezone

from courses.models import Course
from employees.models import Employee

from .models import Enrollment


class EnrollmentFilterForm(forms.Form):
    """Форма фильтрации списка назначений на основе forms.Form."""

    STATUS_CHOICES = [
        ("", "Все"),
        (Enrollment.Status.ACTIVE, "Активные"),
        (Enrollment.Status.CANCELLED, "Отменённые"),
        (Enrollment.Status.COMPLETED, "Завершённые"),
    ]
    SORT_CHOICES = [
        ("deadline", "Сроку (сначала ближайшие)"),
        ("-deadline", "Сроку (сначала поздние)"),
        ("course", "Курсу"),
        ("employee", "Сотруднику"),
    ]

    # Поиск по ФИО сотрудника связанной модели
    q = forms.CharField(
        label="ФИО сотрудника",
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "search",
                "class": "form-control",
                "placeholder": "Например, Иванов",
            }
        ),
    )
    # Django проверит, что выбранный курс существует в базе
    course = forms.ModelChoiceField(
        queryset=Course.objects.order_by("title"),
        required=False,
        label="Курс",
        empty_label="Все курсы",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.order_by("full_name"),
        required=False,
        label="Сотрудник",
        empty_label="Все сотрудники",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    # Допустимы только коды статусов из перечисления модели
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label="Статус",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    deadline = forms.DateField(
        required=False,
        label="Срок сдачи до",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"},
            format="%Y-%m-%d",
        ),
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial="deadline",
        label="Сортировать по",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_q(self):
        # Пользовательская проверка: поиск по одному символу слишком широкий
        query = self.cleaned_data["q"].strip()
        if query and len(query) < 2:
            raise forms.ValidationError(
                "Введите не менее двух символов для поиска."
            )
        return query


class EnrollmentForm(forms.ModelForm):
    """Форма создания и редактирования назначения на основе ModelForm."""

    class Meta:
        model = Enrollment
        fields = [
            "employee",
            "course",
            "deadline",
            "total_questions",
            "lessons_completed",
            "correct_answers",
        ]
        labels = {
            "employee": "Сотрудник",
            "course": "Курс",
            "deadline": "Срок сдачи",
            "total_questions": "Вопросов в тесте",
            "lessons_completed": "Пройдено уроков",
            "correct_answers": "Правильных ответов",
        }
        help_texts = {
            "deadline": "Дата, до которой сотрудник должен пройти курс.",
            "total_questions": "Число вопросов в итоговом тесте курса.",
        }
        widgets = {
            "deadline": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "employee": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "total_questions": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "lessons_completed": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "correct_answers": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        if deadline < timezone.localdate():
            raise forms.ValidationError(
                "Нельзя назначить курс на прошедшую дату."
            )
        return deadline

    def clean(self):
        cleaned = super().clean()
        course = cleaned.get("course")
        lessons_completed = cleaned.get("lessons_completed")
        correct_answers = cleaned.get("correct_answers")
        total_questions = cleaned.get("total_questions")

        if course and lessons_completed is not None:
            if lessons_completed > course.total_lessons:
                self.add_error(
                    "lessons_completed",
                    f"В курсе «{course.title}» всего "
                    f"{course.total_lessons} уроков.",
                )
        if total_questions and correct_answers is not None:
            if correct_answers > total_questions:
                self.add_error(
                    "correct_answers",
                    "Правильных ответов не может быть больше, "
                    "чем вопросов в тесте.",
                )
        return cleaned
