import pytest

from student_grading.data import load_demo_students
from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord
from student_grading.processors import (
    count_subjects,
    filter_items,
    find_student_linear,
    group_by_subject,
    group_by_subject_and_group,
    index_students_by_id,
    index_students_by_name,
    process_pipeline,
    sort_items,
    unique_subjects,
)


@pytest.fixture
def students() -> list[StudentRecord]:
    return load_demo_students()


def test_set_counter_and_grouping(students: list[StudentRecord]) -> None:
    assert unique_subjects(students) == {"Python", "Бази даних"}
    assert count_subjects(students) == {"Python": 3, "Бази даних": 2}
    grouped = group_by_subject(students)
    assert grouped["Python"] == [students[0], students[1], students[3]]

    nested = group_by_subject_and_group(students)
    assert nested["Python"]["ФеП-31"] == [students[1], students[3]]


def test_dict_indexes_and_linear_search(students: list[StudentRecord]) -> None:
    by_id = index_students_by_id(students)
    by_name = index_students_by_name(students)

    assert by_id[3] is students[2]
    assert by_name["ірина бондар"] is students[2]
    assert find_student_linear(students, 3) is students[2]
    assert find_student_linear(students, 999) is None


def test_id_index_rejects_missing_or_duplicate_ids() -> None:
    missing = StudentRecord("Без ID", "Python", [80])
    with pytest.raises(GradeValidationError, match="must have an ID"):
        index_students_by_id([missing])

    first = StudentRecord("Один", "Python", [80], student_id=1)
    second = StudentRecord("Два", "Python", [90], student_id=1)
    with pytest.raises(GradeValidationError, match="unique"):
        index_students_by_id([first, second])


def test_higher_order_filter_sort_and_pipeline(
    students: list[StudentRecord],
) -> None:
    result = process_pipeline(
        students,
        lambda records: filter_items(
            records,
            lambda student: student.average_grade >= 75,
        ),
        lambda records: sort_items(
            records,
            key=lambda student: student.average_grade,
            reverse=True,
        ),
    )

    assert [student.student_id for student in result] == [3, 1, 2]
