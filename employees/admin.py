from django.contrib import admin
from django.db.models import Count, Q

from enrollments.models import Enrollment

from .models import Employee


class EnrollmentInline(admin.TabularInline):
    # Назначения, связанные с текущим сотрудником
    model = Enrollment
    fields = ("course", "deadline", "status", "lessons_completed")
    readonly_fields = ("course", "deadline")
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "department", "active_enrollments_count")
    list_display_links = ("full_name",)
    search_fields = ("full_name", "department")
    list_filter = ("department",)
    ordering = ("full_name",)
    list_per_page = 10
    readonly_fields = ("id",)
    inlines = (EnrollmentInline,)

    @admin.display(description="Активные назначения")
    def active_enrollments_count(self, obj: Employee) -> int:
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
