from django.shortcuts import render

from models.courses import find_course_by_id
from storage import load_courses

COURSES_FILE = "data/courses.json"


def courses(request):
    context = {
        "courses": load_courses(COURSES_FILE),
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request, course_id):
    course = find_course_by_id(load_courses(COURSES_FILE), course_id)
    context = {
        "course": course,
    }
    return render(
        request,
        "courses/course_detail.html",
        context,
        status=404 if course is None else 200,
    )
