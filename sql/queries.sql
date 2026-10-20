-- ==========================================
-- Сервис обучения сотрудников: SQL-запросы проекта
-- База: data/training.sqlite
-- Значения в запросах 3, 7 и 8 даны для проверки в SQLite CLI;
-- в Django они передаются параметром ?
-- ==========================================

-- 1. Список курсов (выборка списка) — страница /courses/
SELECT id, title, category, total_lessons
FROM courses
ORDER BY title;

-- 2. Список сотрудников (выборка списка) — выпадающий список на /courses/available/
SELECT id, full_name, department
FROM employees
ORDER BY full_name;

-- 3. Курсы длительностью не меньше заданного числа уроков (WHERE)
SELECT id, title, total_lessons
FROM courses
WHERE total_lessons >= 8
ORDER BY total_lessons;

-- 4. Активные (не отменённые) назначения (WHERE)
SELECT id, course_id, employee_id, deadline
FROM enrollments
WHERE is_cancelled = 0
ORDER BY deadline;

-- 5. Все назначения с названием курса и ФИО сотрудника (JOIN) — страница /enrollments/
SELECT
    enrollments.id,
    enrollments.deadline,
    enrollments.is_cancelled,
    courses.title AS course_title,
    employees.full_name AS employee_name
FROM enrollments
JOIN courses ON enrollments.course_id = courses.id
JOIN employees ON enrollments.employee_id = employees.id
ORDER BY enrollments.deadline;

-- 6. Просроченные незавершённые назначения (JOIN + WHERE по нескольким условиям)
SELECT
    enrollments.id,
    employees.full_name AS employee_name,
    courses.title AS course_title,
    enrollments.deadline,
    enrollments.lessons_completed,
    courses.total_lessons
FROM enrollments
JOIN courses ON enrollments.course_id = courses.id
JOIN employees ON enrollments.employee_id = employees.id
WHERE enrollments.is_cancelled = 0
  AND enrollments.deadline < date('now')
  AND enrollments.lessons_completed < courses.total_lessons;

-- 7. Активные назначения одного сотрудника (JOIN + WHERE)
SELECT
    courses.title AS course_title,
    enrollments.deadline,
    enrollments.lessons_completed,
    courses.total_lessons
FROM enrollments
JOIN courses ON enrollments.course_id = courses.id
WHERE enrollments.employee_id = 1
  AND enrollments.is_cancelled = 0
ORDER BY enrollments.deadline;

-- 8. Курсы, которые ещё можно назначить сотруднику (подзапрос NOT IN) — страница /courses/available/
SELECT id, title, category, total_lessons
FROM courses
WHERE id NOT IN (
    SELECT course_id
    FROM enrollments
    WHERE employee_id = 2
      AND is_cancelled = 0
)
ORDER BY title;

-- 9. Количество активных назначений (агрегатная функция COUNT)
SELECT COUNT(*) AS active_count
FROM enrollments
WHERE is_cancelled = 0;

-- 10. Сводка по курсам: количество, мин., макс., средняя и общая длительность (агрегатные функции)
SELECT
    COUNT(*) AS courses_count,
    MIN(total_lessons) AS min_lessons,
    MAX(total_lessons) AS max_lessons,
    ROUND(AVG(total_lessons), 1) AS avg_lessons,
    SUM(total_lessons) AS sum_lessons
FROM courses;

-- 11. Количество активных назначений по каждому курсу (LEFT JOIN + GROUP BY) — /enrollments/statistics/
SELECT
    courses.title AS course_title,
    COUNT(enrollments.id) AS enrollments_count
FROM courses
LEFT JOIN enrollments
    ON courses.id = enrollments.course_id
    AND enrollments.is_cancelled = 0
GROUP BY courses.id, courses.title
ORDER BY enrollments_count DESC, courses.title;

-- 12. Количество назначений по отделам (JOIN + GROUP BY) — /enrollments/statistics/
SELECT
    employees.department,
    COUNT(enrollments.id) AS enrollments_count
FROM enrollments
JOIN employees ON enrollments.employee_id = employees.id
WHERE enrollments.is_cancelled = 0
GROUP BY employees.department
ORDER BY enrollments_count DESC;

-- 13. Курсы, на которые назначено больше одного сотрудника (GROUP BY + HAVING) — /enrollments/statistics/
SELECT
    courses.title AS course_title,
    COUNT(enrollments.id) AS enrollments_count
FROM courses
JOIN enrollments ON courses.id = enrollments.course_id
WHERE enrollments.is_cancelled = 0
GROUP BY courses.id, courses.title
HAVING COUNT(enrollments.id) > 1
ORDER BY enrollments_count DESC;

-- 14. Три ближайших срока сдачи (ORDER BY + LIMIT)
SELECT id, course_id, employee_id, deadline
FROM enrollments
WHERE is_cancelled = 0
ORDER BY deadline
LIMIT 3 OFFSET 0;
