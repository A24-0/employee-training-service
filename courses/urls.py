from django.urls import path

from . import views

urlpatterns = [
    path("", views.courses, name="courses"),
    path("<str:course_id>/", views.course_detail, name="course_detail"),
]
