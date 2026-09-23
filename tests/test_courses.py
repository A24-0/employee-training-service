from courses import (
    add_course,
    check_course_lessons,
    filter_courses_by_category,
    find_course,
    sort_courses,
)


def test_add_course():
    courses = []
    add_course(courses, "Основы Python", "Разработка", 10)
    assert len(courses) == 1
    assert courses[0]["id"] == 1


def test_find_course():
    courses = []
    add_course(courses, "Основы Python", "Разработка", 10)
    assert find_course(courses, "python")


def test_check_course_lessons():
    courses = []
    course = add_course(courses, "Основы Python", "Разработка", 10)
    assert check_course_lessons(course, 5)
    assert not check_course_lessons(course, 20)


def test_filter_courses_by_category():
    courses = []
    add_course(courses, "Основы Python", "Разработка", 10)
    add_course(courses, "Тестирование ПО", "QA", 8)
    assert len(filter_courses_by_category(courses, "QA")) == 1


def test_sort_courses():
    courses = []
    add_course(courses, "Курс А", "Разработка", 10)
    add_course(courses, "Курс Б", "Разработка", 5)
    sorted_courses = sort_courses(courses)
    assert sorted_courses[0]["total_lessons"] == 5
