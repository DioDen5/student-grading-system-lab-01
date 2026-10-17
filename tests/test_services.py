import pytest

from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord
from student_grading.services import (
    PerformanceLevel,
    add_student,
    calculate_average,
    calculate_statistics,
    determine_performance,
    find_min_max_grades,
    find_students_above_average,
    is_successful,
    search_students,
    sort_students,
)


@pytest.fixture
def students() -> list[StudentRecord]:
    return [
        StudentRecord("Анна Коваль", "Python", [95, 85], group="ФеП-32"),
        StudentRecord("Олег Мельник", "Python", [70, 80], group="ФеП-31"),
        StudentRecord("Ірина Бондар", "Бази даних", [55, 60], group="ФеП-32"),
    ]


def test_add_student(students: list[StudentRecord]) -> None:
    new_student = StudentRecord("Марія Левченко", "Python", [88])

    add_student(students, new_student)

    assert students[-1] is new_student


def test_required_grade_calculations(students: list[StudentRecord]) -> None:
    assert calculate_average(students[0]) == 90
    assert find_min_max_grades(students[0]) == (85, 95)


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (90, PerformanceLevel.EXCELLENT),
        (75, PerformanceLevel.GOOD),
        (60, PerformanceLevel.SATISFACTORY),
        (59.99, PerformanceLevel.FAILING),
    ],
)
def test_performance_boundaries(
    grade: float,
    expected: PerformanceLevel,
) -> None:
    student = StudentRecord("Тестовий Студент", "Python", [grade])

    assert determine_performance(student) is expected
    assert is_successful(student) is (grade >= 60)


def test_sort_students_does_not_modify_input(students: list[StudentRecord]) -> None:
    original = students.copy()

    result = sort_students(students)

    assert [student.average_grade for student in result] == [90, 75, 57.5]
    assert students == original
    assert [student.average_grade for student in sort_students(students, descending=False)] == [
        57.5,
        75,
        90,
    ]


def test_find_students_strictly_above_threshold(
    students: list[StudentRecord],
) -> None:
    assert find_students_above_average(students, 75) == [students[0]]
    assert find_students_above_average(students, 70, subject="python") == students[:2]


@pytest.mark.parametrize("threshold", [-1, 101, float("inf"), "x"])
def test_invalid_threshold_raises(threshold: object, students: list[StudentRecord]) -> None:
    with pytest.raises(GradeValidationError):
        find_students_above_average(students, threshold)  # type: ignore[arg-type]


def test_search_by_multiple_criteria(students: list[StudentRecord]) -> None:
    assert search_students(
        students,
        name_query="ков",
        subject="PYTHON",
        minimum_average=80,
    ) == [students[0]]
    assert search_students(students, group="феп-32") == [students[0], students[2]]


def test_statistics(students: list[StudentRecord]) -> None:
    statistics = calculate_statistics(students)

    assert statistics.record_count == 3
    assert statistics.overall_average == pytest.approx(74.1666667)
    assert statistics.minimum_grade == 55
    assert statistics.maximum_grade == 95
    assert statistics.successful_count == 2


def test_statistics_rejects_empty_collection() -> None:
    with pytest.raises(GradeValidationError):
        calculate_statistics([])
