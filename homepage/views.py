from django.http import HttpResponse

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
    "/dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body>
    <nav class="nav">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/courses/">Курсы</a>
        <a class="nav-link" href="/enrollments/">Назначения</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request):
    content = """
    <h1 class="display-4">Сервис обучения сотрудников</h1>
    <p class="lead">Учёт курсов и прохождения обучения сотрудниками.</p>
    <p>Основные разделы:</p>
    <a href="/courses/" class="btn btn-primary me-2">Курсы</a>
    <a href="/enrollments/" class="btn btn-secondary">Назначения</a>
    """
    return HttpResponse(page("Сервис обучения сотрудников", content))
