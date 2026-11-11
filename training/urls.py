from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from homepage.views import page_not_found

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

# Неизвестный адрес с завершающим слэшем показывает страницу проекта.
# Адреса без слэша обрабатывает APPEND_SLASH, поэтому шаблон требует "/" в конце
urlpatterns.append(re_path(r"^.*/$", page_not_found))

# Обработчик 404 для режима DEBUG = False
handler404 = "homepage.views.page_not_found"
