from django.urls import path

from . import views

app_name = "enrollments"

urlpatterns = [
    path("", views.enrollments, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("create/", views.enrollment_create, name="create"),
    path("<int:enrollment_id>/", views.enrollment_detail, name="detail"),
    path("<int:enrollment_id>/edit/", views.enrollment_edit, name="edit"),
    path("<int:enrollment_id>/cancel/", views.enrollment_cancel, name="cancel"),
]
