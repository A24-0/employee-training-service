from typing import List, Optional


class Course:

    def __init__(
        self,
        course_id: int,
        title: str,
        category: str,
        total_lessons: int,
    ) -> None:
        self.id = course_id
        self.title = title
        self.category = category
        self.total_lessons = total_lessons

    def has_at_least(self, min_lessons: int) -> bool:
        return self.total_lessons >= min_lessons

    @classmethod
    def from_data(cls, data: dict) -> "Course":
        return cls(
            data["id"],
            data["title"],
            data["category"],
            data["total_lessons"],
        )

    def __str__(self) -> str:
        return (
            f"[{self.id}] Курс: {self.title} ({self.category}), "
            f"всего уроков: {self.total_lessons}"
        )


def add_course(
    courses: List[Course],
    title: str,
    category: str,
    total_lessons: int,
) -> Course:
    course_id = max((c.id for c in courses), default=0) + 1
    course = Course(course_id, title, category, total_lessons)
    courses.append(course)
    return course


def find_course(courses: List[Course], query: str) -> List[Course]:
    query = query.lower()
    return [c for c in courses if query in c.title.lower()]


def find_course_by_id(
    courses: List[Course],
    course_id: int,
) -> Optional[Course]:
    for course in courses:
        if course.id == course_id:
            return course
    return None


def filter_courses_by_category(
    courses: List[Course],
    category: str,
) -> List[Course]:
    category = category.lower()
    return [c for c in courses if c.category.lower() == category]


def sort_courses(courses: List[Course]) -> List[Course]:
    return sorted(courses, key=lambda c: c.total_lessons)


def show_courses(courses: List[Course]) -> None:
    if not courses:
        print("Курсы не найдены")
        return
    for course in courses:
        print(course)
