import json

import pytest

from student_grading.analytics import (
    aggregate_by_subject,
    build_summary,
    calculate_average_values,
    create_average_filter,
    create_student_record,
    export_summary,
    grade_distribution,
)
from student_grading.data import load_demo_students
from student_grading.exceptions import GradeValidationError


def test_args_kwargs_closure_and_counter() -> None:
    students = load_demo_students()
    created = create_student_record(
        full_name="Тестовий Студент",
        subject="Python",
        grades=[80, 90],
        group="ФеП-32",
        student_id=99,
    )

    assert calculate_average_values(70, 80, 90) == 80
    assert calculate_average_values() == 0
    assert create_average_filter(85)(created) is True
    assert grade_distribution(students)[92.0] == 1
    assert build_summary(answer=42) == {"answer": 42}


@pytest.mark.parametrize("values", [(-1,), (101,)])
def test_average_values_rejects_invalid_grades(
    values: tuple[float, ...],
) -> None:
    with pytest.raises(GradeValidationError):
        calculate_average_values(*values)


def test_closure_rejects_invalid_threshold() -> None:
    with pytest.raises(GradeValidationError):
        create_average_filter(101)


def test_subject_aggregation_and_json_export(tmp_path) -> None:
    students = load_demo_students()
    statistics = aggregate_by_subject(students)

    assert statistics["Python"].record_count == 3
    assert statistics["Бази даних"].minimum_grade == 48

    output = export_summary(tmp_path / "summary.json", students)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["variant"] == 7
    assert payload["laboratory_work"] == 2
    assert payload["record_count"] == 5
