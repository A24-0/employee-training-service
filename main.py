from datetime import date

employee_name = "Иванов Иван Иванович"
mail = "ivanov@example.com"
department = "Отдел контроля качества"
position = "Ручное тестирование"

course_name = "Ручное тестирование программного обеспечения для начинающих"
course_category = "Тестирование"
total_lessons = 10
lessons_completed = 10
deadline = date(2026, 9, 30)
today = date.today()

total_questions = 20
correct_answers = 17

accuracy = (correct_answers / total_questions) * 100 
accuracy_rounded = int(accuracy)

all_lessons_done = lessons_completed == total_lessons
test_passed = accuracy >= 80
is_on_time = today <= deadline

def get_learning_status(all_lessons_done, test_passed, is_on_time, accuracy_rounded):
    if not all_lessons_done:
        return "Курс не завершён: не все уроки пройдены"
    if not test_passed:
        return f"Тест не сдан. Результат: {accuracy_rounded}% (порог — 80%)"
    if not is_on_time:
        return "Курс пройден, но с нарушением сроков"
    if accuracy_rounded >= 90:
        return "Курс пройден на отлично! Сертификат выдан."
    return "Курс пройден успешно. Сертификат выдан."

status = get_learning_status(all_lessons_done, test_passed, is_on_time, accuracy_rounded)

days_left = (deadline - today).days
bonus_points = int(days_left * 0.25)
total_points = accuracy_rounded + bonus_points

print(f"Сотрудник: {employee_name}")
print(f"Почта: {mail}")
print(f"Отдел: {department}")
print(f"Должность: {position}")
print(f"Курс: {course_name}")
print(f"Категория: {course_category}")
print(f"Дедлайн: {deadline}")
print(f"Сегодня: {today}")
print(f"Осталось дней: {days_left}")
print(f"Уроков пройдено: {lessons_completed} из {total_lessons}")
print(f"Правильных ответов: {correct_answers} из {total_questions}")
print(f"Точность: {accuracy_rounded}%")
print(f"Бонус за выполение в срок: {bonus_points} баллов")
print(f"Итого баллов: {total_points}")
print(f"Статус: {status}")