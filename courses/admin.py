from django.contrib import admin
from django.db.models import Count, Q

from enrollments.models import Enrollment

from .models import Course


class EnrollmentInline(admin.TabularInline):
    # Назначения, связанные с текущим курсом
    model = Enrollment
    fields = ("employee", "deadline", "status", "lessons_completed")
    readonly_fields = ("employee", "deadline")
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "total_lessons",
        "is_long",
        "active_enrollments_count",
    )
    list_display_links = ("title",)
    list_editable = ("total_lessons",)
    search_fields = ("title", "category")
    list_filter = ("category", "is_long")
    ordering = ("title",)
    list_per_page = 10
    readonly_fields = ("id", "slug", "is_long")
    inlines = (EnrollmentInline,)

    @admin.display(description="Активные назначения")
    def active_enrollments_count(self, obj: Course) -> int:
        # Число активных назначений считает база данных (annotate)
        return obj.active_count

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                active_count=Count(
                    "enrollments",
                    filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
                )
            )
        )
