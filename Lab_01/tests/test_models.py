import math

import pytest

from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord


def test_student_record_normalizes_text_and_grades() -> None:
    student = StudentRecord("  Анна Коваль ", " Python ", [90, 80.5, 70])

    assert student.full_name == "Анна Коваль"
    assert student.subject == "Python"
    assert student.grades == (90.0, 80.5, 70.0)


def test_grade_properties() -> None:
    student = StudentRecord("Олег Мельник", "Python", [70, 80, 90])

    assert student.average_grade == 80
    assert student.minimum_grade == 70
    assert student.maximum_grade == 90


@pytest.mark.parametrize(
    ("full_name", "subject", "grades"),
    [
        ("", "Python", [80]),
        ("Анна Коваль", "", [80]),
        ("Анна Коваль", "Python", []),
        ("Анна Коваль", "Python", [-1]),
        ("Анна Коваль", "Python", [101]),
        ("Анна Коваль", "Python", [math.inf]),
        ("Анна Коваль", "Python", [math.nan]),
    ],
)
def test_invalid_record_raises_domain_exception(
    full_name: str,
    subject: str,
    grades: list[float],
) -> None:
    with pytest.raises(GradeValidationError):
        StudentRecord(full_name, subject, grades)


def test_non_numeric_grade_preserves_exception_context() -> None:
    with pytest.raises(GradeValidationError) as exception_info:
        StudentRecord("Анна Коваль", "Python", ["not-a-grade"])  # type: ignore[list-item]

    assert isinstance(exception_info.value.__cause__, ValueError)

