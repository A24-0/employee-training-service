from django import forms

from .models import Course


class CourseForm(forms.ModelForm):
    """Форма создания курса с загрузкой обложки."""

    class Meta:
        model = Course
        fields = ["title", "category", "total_lessons", "cover"]
        labels = {
            "title": "Название курса",
            "category": "Категория",
            "total_lessons": "Количество уроков",
            "cover": "Обложка",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "total_lessons": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "cover": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError(
                "Название курса должно содержать не менее трёх символов."
            )
        return title
