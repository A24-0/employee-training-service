from django.urls import path

from . import views

urlpatterns = [
    path("", views.enrollments, name="enrollments"),
    path(
        "<int:enrollment_id>/",
        views.enrollment_detail,
        name="enrollment_detail",
    ),
]
