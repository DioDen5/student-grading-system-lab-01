"""Aggregations, closures, and export helpers for structured grade data."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from student_grading.config import MAX_GRADE, MIN_GRADE
from student_grading.decorators import track_operation
from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord
from student_grading.processors import group_by_subject


@dataclass(frozen=True, slots=True)
class SubjectStatistics:
    """Aggregated values for one academic subject."""

    record_count: int
    grade_count: int
    average_grade: float
    minimum_grade: float
    maximum_grade: float


def calculate_average_values(*values: float) -> float:
    """Calculate an average from a variable number of positional values."""

    if not values:
        return 0.0
    normalized = tuple(float(value) for value in values)
    if any(not MIN_GRADE <= value <= MAX_GRADE for value in normalized):
        raise GradeValidationError(
            f"Grades must be from {MIN_GRADE:g} to {MAX_GRADE:g}."
        )
    return sum(normalized) / len(normalized)


def create_student_record(**fields: Any) -> StudentRecord:
    """Create a validated record from keyword fields."""

    return StudentRecord(**fields)


def create_average_filter(
    minimum_average: float,
) -> Callable[[StudentRecord], bool]:
    """Create a closure that retains an average-grade threshold."""

    threshold = float(minimum_average)
    if not MIN_GRADE <= threshold <= MAX_GRADE:
        raise GradeValidationError(
            f"The average threshold must be from {MIN_GRADE:g} to {MAX_GRADE:g}."
        )

    def predicate(student: StudentRecord) -> bool:
        return student.average_grade >= threshold

    return predicate


def grade_distribution(students: Iterable[StudentRecord]) -> Counter[float]:
    """Count every grade value with Counter."""

    return Counter(
        grade
        for student in students
        for grade in student.grades
    )


@track_operation("aggregate_by_subject")
def aggregate_by_subject(
    students: Iterable[StudentRecord],
) -> dict[str, SubjectStatistics]:
    """Aggregate count, average, minimum, and maximum for each subject."""

    grouped = group_by_subject(students)
    result: dict[str, SubjectStatistics] = {}
    for subject, records in grouped.items():
        grades = [grade for student in records for grade in student.grades]
        result[subject] = SubjectStatistics(
            record_count=len(records),
            grade_count=len(grades),
            average_grade=sum(grades) / len(grades),
            minimum_grade=min(grades),
            maximum_grade=max(grades),
        )
    return result


def build_summary(**fields: object) -> dict[str, object]:
    """Build an extensible summary dictionary from keyword arguments."""

    return dict(fields)


def export_summary(
    path: str | Path,
    students: Iterable[StudentRecord],
) -> Path:
    """Export a JSON summary as an advanced optional capability."""

    records = list(students)
    subject_statistics = aggregate_by_subject(records)
    payload = build_summary(
        variant=7,
        laboratory_work=2,
        record_count=len(records),
        unique_subjects=sorted(subject_statistics),
        subject_statistics={
            subject: asdict(statistics)
            for subject, statistics in subject_statistics.items()
        },
        grade_distribution={
            str(grade): count
            for grade, count in sorted(grade_distribution(records).items())
        },
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output
