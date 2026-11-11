from django.db import migrations

from pytils.translit import slugify


def fill_slugs(apps, schema_editor):
    # Историческая модель, привязанная к состоянию базы на момент миграции
    Course = apps.get_model("courses", "Course")
    used = set()
    for course in Course.objects.order_by("pk"):
        base = slugify(course.title)[:200] or "course"
        candidate = base
        number = 2
        while candidate in used:
            candidate = f"{base}-{number}"
            number += 1
        used.add(candidate)
        Course.objects.filter(pk=course.pk).update(slug=candidate)


def clear_slugs(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    Course.objects.update(slug="")


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0002_course_cover_course_is_long_course_slug_and_more"),
    ]

    operations = [
        migrations.RunPython(fill_slugs, clear_slugs),
    ]
