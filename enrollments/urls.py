from django.urls import path

from . import views

app_name = "enrollments"

urlpatterns = [
    path("", views.enrollments, name="list"),
    path("<int:enrollment_id>/", views.enrollment_detail, name="detail"),
]
