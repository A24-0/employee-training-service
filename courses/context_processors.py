from courses.models import Course
from employees.models import Employee
from enrollments.models import Enrollment


def training_context(request):
    """
    Передаёт общие данные о сервисе обучения в шаблоны.

    request — текущий HTTP-запрос.
    Возвращаемый словарь становится частью контекста шаблона.
    """
    # Количество записей считает база данных, коллекции не загружаются
    return {
        "site_name": "Сервис обучения сотрудников",
        "courses_count": Course.objects.count(),
        "employees_count": Employee.objects.count(),
        "active_enrollments_count": Enrollment.objects.active().count(),
    }
