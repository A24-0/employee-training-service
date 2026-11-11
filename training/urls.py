from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("courses/", include("courses.urls")),
    path("enrollments/", include("enrollments.urls")),
]

if settings.DEBUG:
    # Раздача загруженных обложек в режиме разработки
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    # Панель отладки SQL
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
