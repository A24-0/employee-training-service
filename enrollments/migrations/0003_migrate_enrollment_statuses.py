from django.db import migrations


def migrate_statuses(apps, schema_editor):
    Enrollment = apps.get_model("enrollments", "Enrollment")
    # Отменённые назначения получают статус cancelled,
    # остальные — active, а при пройденных уроках — completed
    Enrollment.objects.filter(is_cancelled=True).update(status="cancelled")
    for enrollment in Enrollment.objects.filter(
        is_cancelled=False
    ).select_related("course"):
        if enrollment.lessons_completed >= enrollment.course.total_lessons:
            new_status = "completed"
        else:
            new_status = "active"
        Enrollment.objects.filter(pk=enrollment.pk).update(status=new_status)


def reverse_statuses(apps, schema_editor):
    Enrollment = apps.get_model("enrollments", "Enrollment")
    # Возвращаем булево поле при откате миграции
    Enrollment.objects.filter(status="cancelled").update(is_cancelled=True)
    Enrollment.objects.exclude(status="cancelled").update(is_cancelled=False)


class Migration(migrations.Migration):

    dependencies = [
        ("enrollments", "0002_enrollment_status_alter_enrollment_deadline"),
    ]

    operations = [
        migrations.RunPython(migrate_statuses, reverse_statuses),
    ]
