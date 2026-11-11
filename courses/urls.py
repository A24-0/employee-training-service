from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.courses, name="list"),
    path("available/", views.available_courses, name="available"),
    path("create/", views.course_create, name="create"),
    path("<slug:slug>/", views.course_detail, name="detail"),
]
