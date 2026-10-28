# Сервис обучения сотрудников

## Назначение
Приложение предназначено для автоматизации процессов корпоративного обучения и развития персонала. Оно решает проблему ручного учета прохождения тренингов, помогает HR-отделам и руководителям контролировать развитие навыков сотрудников, назначать обязательные программы обучения и отслеживать успеваемость в едином цифровом пространстве.

Консольная версия приложения (ПР1–ПР3) дополнена веб-интерфейсом на Django (ПР5), который в ПР6 переведён на систему шаблонов Django: view-функции готовят данные, а HTML формируют шаблоны. В ПР7 данные перенесены в базу SQLite с ручными SQL-запросами, в ПР9 слой доступа к данным переведён на Django ORM.

## Используемые технологии
- Python 3;
- Django 5.2 — веб-фреймворк;
- Django Template Language (DTL) — шаблоны страниц;
- HTML5, CSS3, JavaScript — разметка, собственное оформление и поведение страниц;
- Bootstrap 5.3 — базовая вёрстка (подключается через CDN);
- SQLite — база данных;
- Django ORM — модели, миграции и запросы к базе данных (ПР9);
- модуль `sqlite3` — SQL-слой ПР7 и перенос данных в базу Django;
- JSON — исходные данные и хранилище консольной версии;
- pytest — автоматизированные тесты;
- flake8 — проверка качества кода.

## Целевая аудитория
- **HR-менеджеры и специалисты по обучению (L&D):** для создания учебных программ, назначения курсов и аналитики.
- **Руководители подразделений:** для контроля компетенций своих подчиненных и планирования их развития.
- **Сотрудники компании:** для прохождения курсов, изучения материалов и сдачи итоговых тестирований.

## Предметная область
Предметная область охватывает сферу корпоративного управления человеческими ресурсами (HR Tech) и электронного обучения (e-Learning). Она включает в себя процессы планирования, организации, мониторинга и оценки образовательных мероприятий внутри компании, а также управление компетенциями и ролями персонала.

Сотрудник может иметь несколько назначений на разные курсы. У одного сотрудника не может быть двух активных назначений на один и тот же курс одновременно; отменённое назначение снимает это ограничение.

## Основные сущности
Ниже описаны классы консольной версии (пакет `models/`). Django-модели веб-версии описаны в разделе «Модели Django (ПР9)».

- **Course — курс.** Атрибуты: `id`, `title`, `category`, `total_lessons`. Методы: `has_at_least()` — проверка длительности курса; `from_data()` — создание из данных JSON; `__str__()` — строковое представление.
- **Employee — сотрудник.** Атрибуты: `id`, `full_name`, `department`. Методы: `from_data()` — создание из данных JSON; `__str__()` — строковое представление.
- **Enrollment — назначение курса сотруднику.** Атрибуты: `id`, `course` (объект `Course`), `employee` (объект `Employee`), `deadline`, `total_questions`, `lessons_completed`, `correct_answers`, `is_cancelled`. Методы: `record_progress()` — фиксация прогресса; `cancel()` — отмена назначения; `accuracy()` — точность ответов; `is_lessons_done()`, `is_on_time()` — вспомогательные проверки; `status()` — итоговый текстовый статус; `__str__()` — строковое представление.

`Enrollment` связывает объекты `Course` и `Employee` напрямую (композиция), а не через идентификаторы.

## Страницы веб-интерфейса
- `/` — главная страница: описание приложения и навигация (view-функция `index()`);
- `/courses/?q=<текст>` — список курсов с поиском по названию и категории (view-функция `courses()`);
- `/courses/<int:course_id>/` — страница курса и его активные назначения (view-функция `course_detail()`);
- `/courses/available/?employee=<id>` — подбор курса сотруднику: курсы, на которые он ещё не назначен (view-функция `available_courses()`);
- `/enrollments/` — список назначений курсов с поиском, фильтрацией, сортировкой и постраничным выводом (view-функция `enrollments()`, параметры описаны в разделе «Список назначений»);
- `/enrollments/<int:enrollment_id>/` — страница назначения, включая итоговый статус `enrollment.status()` (view-функция `enrollment_detail()`);
- `/enrollments/statistics/` — статистика обучения (view-функция `statistics()`).

С ПР9 все страницы получают данные из базы Django `db.sqlite3` через Django ORM.

Если курс или назначение с указанным идентификатором не найдено, `get_object_or_404()` возвращает ответ 404; при `DEBUG = False` выводится шаблон `templates/404.html`. Некорректные параметры запроса (дата, номер страницы, поле сортировки, сотрудник) не приводят к ошибке сервера: выводится сообщение или используется значение по умолчанию.

Все страницы формируются Django-шаблонами через `render(request, "шаблон.html", context)`. Генерация HTML в Python-коде веб-представлений не используется; функция `page()` из ПР5 удалена.

## Django Template Language

### Базовый шаблон и наследование
Общий каркас страниц — `templates/base.html` (каталог шаблонов уровня проекта подключён в `settings.py` через `TEMPLATES["DIRS"] = [BASE_DIR / "templates"]`). В нём находятся объявление документа, подключение Bootstrap, собственного CSS и JavaScript, шапка с логотипом, навигация и подвал. Дочерние шаблоны начинаются с `{% extends "base.html" %}` и переопределяют блоки:
- `{% block title %}` — заголовок вкладки браузера;
- `{% block content %}` — содержимое страницы.

### Включаемые шаблоны
Повторяющиеся фрагменты вынесены в отдельные файлы и подключаются через `{% include %}`:
- `templates/includes/navigation.html` — навигация сайта (подсвечивает текущий раздел по `request.resolver_match.namespace`);
- `courses/includes/course_card.html` — карточка одного курса в списке;
- `enrollments/includes/enrollment_status.html` — бейдж статуса назначения «Активно» / «Отменено»; используется и в списке, и на странице назначения.

### Контекст, циклы и условия
View-функции передают данные в шаблон через словарь контекста, например:
```python
context = {"courses": Course.objects.order_by("title")}
return render(request, "courses/course_list.html", context)
```
В шаблонах используются:
- `{% for course in courses %} … {% empty %} … {% endfor %}` — вывод списков и обработка пустой коллекции;
- `{% if enrollment.is_cancelled %}` — отображение статуса назначения;
- `{% if course %} … {% else %} … {% endif %}` — страница «не найдено»;
- `{% if enrollment.is_lessons_done %}` — отметка о прохождении всех уроков.

### Фильтры
- `{{ courses|length }}`, `{{ enrollments|length }}` — количество элементов;
- `{{ course.title|default:"Без названия" }}`, `{{ enrollment.employee.department|default:"отдел не указан" }}` — значение по умолчанию;
- `{{ enrollment.deadline|date:"d.m.Y" }}` — формат даты срока сдачи (`deadline` — объект `date`, поле `DateField`).

Фильтры используются только для представления данных; бизнес-логика (расчёт итогового статуса, точности ответов) остаётся в классах `Enrollment` и `EnrollmentStatus`.

## URL-маршрутизация
Для каждого приложения задано пространство имён (`app_name`) и имена маршрутов:

| Имя маршрута | Адрес |
|---|---|
| `homepage:index` | `/` |
| `courses:list` | `/courses/` |
| `courses:detail` | `/courses/<int:course_id>/` |
| `courses:available` | `/courses/available/` |
| `enrollments:list` | `/enrollments/` |
| `enrollments:detail` | `/enrollments/<int:enrollment_id>/` |
| `enrollments:statistics` | `/enrollments/statistics/` |

Все ссылки в шаблонах строятся через `{% url %}`, например `{% url 'courses:detail' course.id %}`; жёстко заданные адреса не используются.

## Статические файлы
Статические файлы проекта лежат в `homepage/static/homepage/` и подключаются в `base.html` после `{% load static %}`:
- `css/style.css` — собственные стили: шапка, логотип, активный пункт меню, карточки курсов (`.course-card`), статусы назначений (`.enrollment-status`), подвал;
- `js/main.js` — выводит текущий год в подвале страницы;
- `img/logo.png` — логотип сервиса в шапке.

Проверка поиска статического файла: `python manage.py findstatic homepage/img/logo.png`.

## Основные операции

### Используется в веб-интерфейсе
- просмотр списка курсов и поиск курса по названию или категории (ПР9);
- просмотр информации о курсе и его активных назначений (ПР9);
- подбор курсов, которые ещё можно назначить выбранному сотруднику (ПР7);
- просмотр списка назначений курсов: поиск по ФИО, фильтрация, сортировка, постраничный вывод (ПР9);
- просмотр информации о назначении, включая итоговый статус прохождения;
- статистика обучения (ПР7).

### Отложено до следующих работ
Эти операции реализованы в ПР2–ПР3 и работают в консольной версии. В веб-интерфейсе они появятся, когда будут добавлены формы и POST-запросы:
- добавление курса;
- добавление сотрудника;
- назначение курса сотруднику;
- обновление прогресса прохождения курса;
- отмена назначения курса.

## Хранение данных

### JSON (ПР2–ПР6)
Исходные данные лежат в JSON-файлах `data/courses.json`, `data/employees.json`, `data/enrollments.json`. С ними по-прежнему работает консольная версия (`main.py` через `storage.py`). Для связи назначения с курсом и сотрудником в `enrollments.json` используются идентификаторы `course_id` и `employee_id`.

### База данных SQLite (ПР7)
В ПР7 веб-версия работала с базой `data/training.sqlite`: запросы писались на SQL и выполнялись через стандартный модуль `sqlite3`. С ПР9 эта база используется только как источник для переноса данных в базу Django; SQL-слой ПР7 (`sql/`, `db/database.py`, `db/import_json.py`) сохранён в проекте как предыдущая реализация, представления его не используют.

Таблица `courses`:

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER | первичный ключ |
| `title` | TEXT | название курса |
| `category` | TEXT | категория |
| `total_lessons` | INTEGER | количество уроков |

Таблица `employees`:

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER | первичный ключ |
| `full_name` | TEXT | ФИО |
| `department` | TEXT | отдел |

Таблица `enrollments`:

| Поле | Тип | Назначение |
|---|---|---|
| `id` | INTEGER | первичный ключ |
| `course_id` | INTEGER | внешний ключ → `courses.id` |
| `employee_id` | INTEGER | внешний ключ → `employees.id` |
| `deadline` | TEXT | срок сдачи в формате `YYYY-MM-DD` |
| `lessons_completed` | INTEGER | пройдено уроков |
| `correct_answers` | INTEGER | правильных ответов в тесте |
| `total_questions` | INTEGER | вопросов в тесте |
| `is_cancelled` | INTEGER | 0 — активно, 1 — отменено |

Один курс и один сотрудник могут встречаться во многих назначениях; каждое назначение относится к одному курсу и одному сотруднику. Все поля объявлены `NOT NULL`.

Файлы слоя базы данных:
- `sql/schema.sql` — команды `CREATE TABLE` с первичными и внешними ключами;
- `sql/queries.sql` — 14 проверенных запросов с комментариями: списки, `WHERE`, `JOIN`, подзапрос `NOT IN`, `COUNT/MIN/MAX/AVG/SUM`, `GROUP BY`, `HAVING`, `LIMIT/OFFSET`;
- `db/database.py` — подключение (`PRAGMA foreign_keys = ON`) и функции `fetch_all()` / `fetch_one()`, которые возвращают строки в виде словарей с доступом к полям по имени;
- `db/import_json.py` — создаёт таблицы по `schema.sql` и переносит данные из JSON (`executemany()`, параметры `?`, `commit()` / `rollback()`). Скрипт можно запускать повторно: перед вставкой таблицы очищаются.

Создание базы и перенос данных:
```
python -m db.import_json
```

Значения от пользователя (id сотрудника, курса, назначения) передаются в SQL только параметрами `?`, без f-строк.

### Django ORM (ПР9)
Веб-версия работает с базой `db.sqlite3` (параметр `DATABASES` в `training/settings.py`). Структура таблиц описывается моделями и создаётся миграциями. Файл `db.sqlite3` не хранится в репозитории (`.gitignore`): после клонирования он создаётся командой `migrate` и заполняется скриптом переноса.

Цепочка работы с данными: представление → Django ORM → SQLite → объекты моделей.

#### Модели Django
| Модель | Приложение | Поля | Таблица |
|---|---|---|---|
| `Course` — курс | `courses` | `title` (`CharField`), `category` (`CharField`), `total_lessons` (`PositiveIntegerField`) | `courses_course` |
| `Employee` — сотрудник | `employees` | `full_name` (`CharField`), `department` (`CharField`) | `employees_employee` |
| `Enrollment` — назначение | `enrollments` | `course` (`ForeignKey`), `employee` (`ForeignKey`), `deadline` (`DateField`), `lessons_completed`, `correct_answers`, `total_questions` (`PositiveIntegerField`), `is_cancelled` (`BooleanField`, по умолчанию `False`) | `enrollments_enrollment` |

Первичный ключ `id` Django создаёт автоматически (`BigAutoField`). У каждой модели заданы `__str__()`, `Meta.ordering` и `verbose_name`. Методы моделей:
- `Course.has_at_least()` — проверка длительности курса;
- `Enrollment.record_progress()`, `Enrollment.cancel()` — изменение и сохранение назначения (`save(update_fields=...)`);
- `Enrollment.accuracy()`, `is_lessons_done()`, `is_on_time()`, `status()` — расчёт итогового статуса через `EnrollmentStatus` из пакета `models/`.

#### Связи
- `Enrollment.course` → `Course` и `Enrollment.employee` → `Employee` — связи «многие к одному» (`ForeignKey`), внешние ключи `course_id` и `employee_id` находятся в таблице назначений.
- `on_delete=models.PROTECT` — курс или сотрудника нельзя удалить, пока на них ссылаются назначения: история обучения сохраняется.
- `related_name="enrollments"` — обратная связь: `course.enrollments.all()`, `employee.enrollments.all()`.

#### Миграции
- `courses/migrations/0001_initial.py`, `employees/migrations/0001_initial.py`, `enrollments/migrations/0001_initial.py` — создание таблиц моделей.

```
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

#### Перенос данных из базы ПР7
Выбрана стратегия «таблицы, управляемые Django, и перенос данных»: исходная база `data/training.sqlite` не изменяется, данные переносятся в `db.sqlite3` с сохранением идентификаторов и связей.
- `db/inspect_source_db.py` — только читает исходную базу: выводит таблицы, столбцы, количество записей, проверяет внешние ключи и значения `is_cancelled`;
- `db/import_sqlite_to_orm.py` — переносит курсы, сотрудников, затем назначения через `update_or_create()` в одной транзакции `transaction.atomic()`; дата `YYYY-MM-DD` преобразуется в `date`, `0/1` — в `bool`. Скрипт можно запускать повторно: записи с теми же `id` обновляются, а не дублируются.

```
python db/inspect_source_db.py
python db/import_sqlite_to_orm.py
```
Перед переносом создана резервная копия `data/training_backup.sqlite` (не хранится в репозитории). Ожидаемый результат: 3 курса, 3 сотрудника, 6 назначений.

#### Список назначений
Параметры страницы `/enrollments/` передаются через GET и проверяются в представлении:

| Параметр | Назначение | ORM |
|---|---|---|
| `q` | поиск по ФИО сотрудника | `filter(employee__full_name__iregex=...)` |
| `course` | курс | `filter(course_id=...)` |
| `employee` | сотрудник | `filter(employee_id=...)` |
| `status` | `active` / `cancelled` | `filter(is_cancelled=...)` |
| `deadline` | срок сдачи не позднее даты; некорректная дата — сообщение «Укажите корректную дату» | `filter(deadline__lte=...)` |
| `sort` | `deadline`, `-deadline`, `course`, `employee`; неизвестное значение — сортировка по сроку | `order_by(SORT_FIELDS[sort], "id")` |
| `page` | номер страницы (по 5 записей); некорректный номер — первая или последняя страница | `Paginator.get_page()` |

Поле сортировки выбирается из словаря `SORT_FIELDS`, произвольное значение пользователя в `order_by()` не передаётся. Ссылки пагинации строятся тегом `{% querystring page=... %}`, поэтому фильтры и сортировка сохраняются при переходе между страницами.

Поиск выполняется через `iregex` с `re.escape()`: в SQLite `icontains` не учитывает регистр только для латинских букв, а данные проекта на русском.

#### ORM-запросы проекта
| № | Где | Выражение | Приём |
|---|---|---|---|
| 1 | `courses()` | `Course.objects.order_by("title")` | набор объектов, сортировка по одному полю |
| 2 | `courses()` | `filter(Q(title__iregex=...) \| Q(category__iregex=...))` | поиск по нескольким полям |
| 3 | `course_detail()` | `get_object_or_404(Course, pk=course_id)` | один объект, обработка отсутствия |
| 4 | `course_detail()` | `course.enrollments.filter(is_cancelled=False).select_related("employee")` | обратная связь, `select_related()` |
| 5 | `available_courses()` | `Employee.objects.filter(pk=...).exists()` | проверка параметра запроса |
| 6 | `available_courses()` | `Enrollment.objects.filter(employee_id=..., is_cancelled=False).values_list("course_id", flat=True)` | фильтрация по нескольким условиям, по внешнему ключу |
| 7 | `available_courses()` | `Course.objects.exclude(pk__in=...)` | исключение записей |
| 8 | `enrollments()` | `filter(employee__full_name__iregex=...)` | поиск по полю связанной модели |
| 9 | `enrollments()` | `filter(course_id=...)`, `filter(employee_id=...)`, `filter(is_cancelled=...)` | цепочка фильтров («И») |
| 10 | `enrollments()` | `filter(deadline__lte=...)` | фильтрация по дате |
| 11 | `enrollments()` | `annotate(course_title=F("course__title"), ...).order_by(..., "id").values(...)` | `F()`, сортировка по полю связанной модели и по нескольким полям, `values()` |
| 12 | `enrollments()` | `Paginator(enrollments_list, 5).get_page(...)` | постраничный вывод |
| 13 | `enrollment_detail()` | `get_object_or_404(Enrollment.objects.select_related("course", "employee"), pk=...)` | связанные объекты одним запросом |
| 14 | `statistics()` | `Course.objects.aggregate(Count, Min, Max, Round(Avg))` | сводные показатели |
| 15 | `statistics()` | `Enrollment.objects.filter(is_cancelled=False).count()` | количество активных назначений |
| 16 | `statistics()` | `Course.objects.annotate(enrollments_count=Count("enrollments", filter=Q(...)))` | показатель для каждого курса, курсы без назначений не теряются (аналог `LEFT JOIN`) |
| 17 | `statistics()` | `values(department=F("employee__department")).annotate(Count("id"))` | группировка по отделам |
| 18 | `statistics()` | `by_course.filter(enrollments_count__gt=1)` | условие на агрегат (аналог `HAVING`) |
| 19 | `statistics()` | `filter(deadline__lt=..., lessons_completed__lt=F("course__total_lessons"))` | сравнение с полем связанной модели |

Отменённые назначения не учитываются в статистике и не мешают снова подобрать сотруднику тот же курс.

## Структура проекта
```text
employee-training-service/
│
├── README.md
├── requirements.txt
├── setup.cfg
├── manage.py
├── main.py
├── storage.py
├── utils.py
│
├── db.sqlite3            # база Django (не в репозитории)
│
├── db/
│   ├── __init__.py
│   ├── database.py
│   ├── import_json.py
│   ├── inspect_source_db.py
│   └── import_sqlite_to_orm.py
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── training/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
│   ├── includes/
│   │   └── navigation.html
│   ├── 404.html
│   └── base.html
│
├── homepage/
│   ├── static/
│   │   └── homepage/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── img/
│   │       │   └── logo.png
│   │       └── js/
│   │           └── main.js
│   ├── templates/
│   │   └── homepage/
│   │       └── index.html
│   ├── migrations/
│   ├── apps.py
│   ├── urls.py
│   └── views.py
│
├── courses/
│   ├── templates/
│   │   └── courses/
│   │       ├── includes/
│   │       │   └── course_card.html
│   │       ├── available.html
│   │       ├── course_detail.html
│   │       └── course_list.html
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── employees/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── apps.py
│   └── models.py
│
├── enrollments/
│   ├── templates/
│   │   └── enrollments/
│   │       ├── includes/
│   │       │   └── enrollment_status.html
│   │       ├── enrollment_detail.html
│   │       ├── enrollment_list.html
│   │       └── statistics.html
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── models/
│   ├── __init__.py
│   ├── courses.py
│   ├── employees.py
│   ├── enrollments.py
│   └── status.py
│
├── data/
│   ├── courses.json
│   ├── employees.json
│   ├── enrollments.json
│   └── training.sqlite
│
└── tests/
    ├── test_courses.py
    ├── test_database.py
    ├── test_employees.py
    └── test_enrollments.py
```

## Назначение модулей

### `main.py`
Консольная версия приложения (сохранена с ПР3). Отвечает за запуск консольного меню, получение данных от пользователя и организацию пользовательских сценариев.

### `training/`
Пакет настроек Django-проекта: `settings.py` — настройки проекта (в т. ч. `INSTALLED_APPS` и база `db.sqlite3` в `DATABASES`); `urls.py` — маршрутизация верхнего уровня (подключает `homepage`, `courses`, `enrollments` через `include()`); `asgi.py`, `wsgi.py` — точки взаимодействия с сервером.

### `homepage/`
Django-приложение, отвечающее за главную страницу: view-функция `index()` формирует страницу из шаблона `homepage/index.html`. Также в приложении хранятся общие статические файлы проекта (CSS, JavaScript, логотип).

### `templates/`
Шаблоны уровня проекта: базовый шаблон `base.html`, навигация `includes/navigation.html` и страница ошибки `404.html`.

### `courses/`
Django-приложение, отвечающее за курсы: `models.py` — модель `Course`; `migrations/` — миграции модели; `views.py` — view-функции `courses()`, `course_detail()` и `available_courses()` (получают данные через ORM); `templates/courses/` — шаблоны страниц; `urls.py` — маршруты приложения (`app_name = "courses"`).

### `employees/`
Django-приложение, отвечающее за сотрудников: `models.py` — модель `Employee`; `migrations/` — миграции модели. Отдельных страниц у приложения нет: сотрудники выводятся на страницах курсов и назначений.

### `enrollments/`
Django-приложение, отвечающее за назначения курсов: `models.py` — модель `Enrollment` со связями на `Course` и `Employee`; `migrations/` — миграции модели; `views.py` — view-функции `enrollments()`, `enrollment_detail()` и `statistics()` (получают данные через ORM); `templates/enrollments/` — шаблоны страниц; `urls.py` — маршруты приложения (`app_name = "enrollments"`).

### `models/`
Классы предметной области консольной версии и функции работы с ними (пакет ПР3): `courses.py` — класс `Course` и функции работы с курсами; `employees.py` — класс `Employee` и функции работы с сотрудниками; `enrollments.py` — класс `Enrollment` и функции работы с назначениями; `status.py` — класс `EnrollmentStatus` (расчёт итогового статуса, используется и Django-моделью `Enrollment`).

### `storage.py`
Отвечает за загрузку и сохранение JSON-данных консольной версии: преобразование JSON → объекты Python и обратно.

### `db/` и `sql/`
Слой базы данных SQLite (ПР7) и скрипты переноса данных в Django ORM (ПР9), описаны в разделе «Хранение данных».

### `utils.py`
Содержит вспомогательные функции консольного ввода: `input_int()`, `input_date()`, `input_str()`.

### `tests/`
Содержит автоматизированные тесты проекта (pytest).

## Требования
- Python 3.x;
- Django 5.2;
- pytest;
- flake8.

Установка зависимостей:
```
pip install -r requirements.txt
```

## Запуск приложения

Веб-версия (Django):
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python db/import_sqlite_to_orm.py
python manage.py runserver
```
`migrate` создаёт таблицы в `db.sqlite3`, `import_sqlite_to_orm.py` переносит в них данные из `data/training.sqlite`. Если исходной базы ПР7 нет или данные в JSON изменились, сначала выполнить `python -m db.import_json`.
После запуска открыть в браузере адрес `http://127.0.0.1:8000/`.

Консольная версия (сохранена):
```
python main.py
```

## Проверка проекта
```
python manage.py check
python manage.py makemigrations --check
python manage.py showmigrations
```

## Тестирование
```
pytest
```

## Проверка качества кода
```
flake8
```

## Git
Исходный код проекта хранится в Git-репозитории.

## Текущее состояние и план развития

Реализовано (ПР5):
- Django-проект и три Django-приложения (`homepage`, `courses`, `enrollments`);
- маршрутизация URL двух уровней;
- view-функции и страницы;
- отображение данных предметной области (курсы и назначения);
- навигация между страницами;
- оформление Bootstrap 5.3.

Реализовано (ПР6):
- переход на Django Template Language, отказ от функции `page()`;
- базовый шаблон `base.html`, наследование (`extends`) и блоки (`block`);
- включаемые шаблоны (`include`): навигация, карточка курса, статус назначения;
- передача данных через контекст, циклы `for … empty` и условия `if`;
- пространства имён URL и ссылки через `{% url %}`;
- фильтры `length`, `default`, `date`;
- статические файлы: собственный CSS, JavaScript и логотип.

Реализовано (ПР7):
- спроектирована база SQLite: таблицы `courses`, `employees`, `enrollments`, первичные и внешние ключи;
- схема в `sql/schema.sql`, перенос данных из JSON скриптом `db/import_json.py`;
- 14 SQL-запросов в `sql/queries.sql`;
- view-функции получают данные из SQLite через `sqlite3` и `sqlite3.Row`;
- новые страницы: подбор курса сотруднику и статистика обучения.

Реализовано (ПР9):
- модели Django `Course`, `Employee`, `Enrollment` в приложениях `courses`, `employees`, `enrollments`;
- связи `ForeignKey` с `on_delete=PROTECT` и `related_name="enrollments"`;
- миграции, создание таблиц в `db.sqlite3`;
- перенос данных из `data/training.sqlite` с сохранением идентификаторов и связей;
- все представления получают данные через Django ORM, прямых SQL-запросов в представлениях нет;
- поиск курсов и назначений, фильтрация, сортировка и постраничный вывод списка назначений;
- статистика через `aggregate()` и `annotate()`.

Формы в текущей версии не используются.

Планируется:
- формы создания курсов, назначений и обновления прогресса;
- реализация пользователей (аутентификация сотрудников);
- разработка API;
- контейнеризация приложения;
- настройка CI/CD.

![Студент](https://img.shields.io/badge/Студент-Гришутина_А.В.-blue)
![Группа](https://img.shields.io/badge/Группа-ЭФБО--17--24-green)
