from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.courses, name="list"),
    path("available/", views.available_courses, name="available"),
    path("<int:course_id>/", views.course_detail, name="detail"),
]
