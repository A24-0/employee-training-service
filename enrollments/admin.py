from django.contrib import admin, messages

from .models import Enrollment


@admin.action(description="Отменить выбранные назначения")
def cancel_enrollments(modeladmin, request, queryset):
    updated = queryset.update(status=Enrollment.Status.CANCELLED)
    modeladmin.message_user(
        request,
        f"Отменено назначений: {updated}.",
        messages.SUCCESS,
    )


@admin.action(description="Отметить выбранные назначения завершёнными")
def complete_enrollments(modeladmin, request, queryset):
    updated = queryset.update(status=Enrollment.Status.COMPLETED)
    modeladmin.message_user(
        request,
        f"Завершено назначений: {updated}.",
        messages.SUCCESS,
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "course",
        "course_total_lessons",
        "deadline",
        "status",
        "lessons_completed",
        "accuracy_percent",
    )
    list_display_links = ("id", "employee")
    search_fields = ("employee__full_name", "course__title")
    list_filter = ("status", "course", "deadline")
    ordering = ("-deadline",)
    list_per_page = 20
    list_select_related = ("course", "employee")
    readonly_fields = ("id", "accuracy_percent")
    date_hierarchy = "deadline"
    actions = (cancel_enrollments, complete_enrollments)

    @admin.display(description="Уроков в курсе", ordering="course__total_lessons")
    def course_total_lessons(self, obj: Enrollment) -> int:
        # Поле связанной таблицы: list_select_related исключает N+1
        return obj.course.total_lessons

    @admin.display(description="Результат теста")
    def accuracy_percent(self, obj: Enrollment) -> str:
        return f"{obj.accuracy()}%"
