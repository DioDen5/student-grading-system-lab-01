"""Deterministic structured data used by demonstrations and tests."""

from student_grading.models import StudentRecord


GRADE_RANGE: tuple[float, float] = (0.0, 100.0)
DEMO_GROUPS: tuple[str, ...] = ("ФеП-31", "ФеП-32")


def load_demo_students() -> list[StudentRecord]:
    """Return a fresh list of variant 7 records for laboratory work 2."""

    return [
        StudentRecord(
            "Анна Коваль",
            "Python",
            (92, 88, 95, 91),
            group="ФеП-32",
            student_id=1,
        ),
        StudentRecord(
            "Олег Мельник",
            "Python",
            (72, 76, 81, 79),
            group="ФеП-31",
            student_id=2,
        ),
        StudentRecord(
            "Ірина Бондар",
            "Бази даних",
            (96, 94, 98, 97),
            group="ФеП-32",
            student_id=3,
        ),
        StudentRecord(
            "Андрій Шевченко",
            "Python",
            (58, 63, 61, 60),
            group="ФеП-31",
            student_id=4,
        ),
        StudentRecord(
            "Марія Левченко",
            "Бази даних",
            (48, 55, 52, 57),
            group="ФеП-32",
            student_id=5,
        ),
    ]
