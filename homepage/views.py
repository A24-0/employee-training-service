from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "homepage/index.html")


def page_not_found(request: HttpRequest, exception=None) -> HttpResponse:
    # Страница проекта для отсутствующих объектов и неизвестных адресов
    return render(request, "404.html", status=404)
