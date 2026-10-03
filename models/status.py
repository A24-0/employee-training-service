class EnrollmentStatus:
    PASS_THRESHOLD = 80
    EXCELLENT_THRESHOLD = 90

    @staticmethod
    def check_lessons_completion(lessons_completed: int, total: int) -> str:
        if lessons_completed == total:
            return "Все уроки пройдены"
        return f"Пройдено {lessons_completed} из {total} уроков"

    @classmethod
    def calculate(
        cls,
        accuracy: int,
        is_on_time: bool,
        all_lessons_done: bool,
    ) -> str:
        if not all_lessons_done:
            return "Курс не завершён: не все уроки пройдены"
        if accuracy < cls.PASS_THRESHOLD:
            return (
                f"Тест не сдан. Результат: {accuracy}% "
                f"(порог — {cls.PASS_THRESHOLD}%)"
            )
        if not is_on_time:
            return "Курс пройден, но с нарушением сроков"
        if accuracy >= cls.EXCELLENT_THRESHOLD:
            return "Курс пройден на отлично! Сертификат выдан."
        return "Курс пройден успешно. Сертификат выдан."
