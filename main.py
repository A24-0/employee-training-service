from datetime import date

COURSE_NAME = "Ручное тестирование ПО для начинающих"
COURSE_CATEGORY = "ТESTирование"
TOTAL_LESSONS = 10

EMPLOYEE_NAME = "Иванов Иван Иванович"
DEPARTMENT = "Отдел контроля качества"


def get_course_info(name: str, category: str, lessons: int) -> str:
    """Возвращает строку с информацией о курсе."""
    return f"Курс: {name} ({category}), всего уроков: {lessons}"


def check_lessons_completion(lessons_completed: int, total: int) -> str:
    """Проверяет, все ли уроки пройдены."""
    if lessons_completed == total:
        return "Все уроки пройдены"
    return f"Пройдено {lessons_completed} из {total} уроков"


def calculate_status(accuracy: int, is_on_time: bool, all_lessons_done: bool) -> str:
    """Определяет итоговый статус прохождения курса."""
    if not all_lessons_done:
        return "Курс не завершён: не все уроки пройдены"
    if accuracy < 80:
        return f"Тест не сдан. Результат: {accuracy}% (порог — 80%)"
    if not is_on_time:
        return "Курс пройден, но с нарушением сроков"
    if accuracy >= 90:
        return "Курс пройден на отлично! Сертификат выдан."
    return "Курс пройден успешно. Сертификат выдан."


def main() -> None:
    """Основной сценарий программы."""
    print(get_course_info(COURSE_NAME, COURSE_CATEGORY, TOTAL_LESSONS))
    
    lessons_completed = 10
    correct_answers = 17
    total_questions = 20
    deadline = date(2026, 9, 30)
    today = date.today()
    
    all_lessons_done = (lessons_completed == TOTAL_LESSONS)
    accuracy = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    is_on_time = (today <= deadline)
    
    status = calculate_status(accuracy, is_on_time, all_lessons_done)
    lessons_status = check_lessons_completion(lessons_completed, TOTAL_LESSONS)
    
    print(f"\nСотрудник: {EMPLOYEE_NAME} ({DEPARTMENT})")
    print(f"Прогресс: {lessons_status}")
    print(f"Точность ответов: {accuracy}%")
    print(f"Итоговый статус: {status}")


if __name__ == "__main__":
    main()