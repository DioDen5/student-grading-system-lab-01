"""Business logic for calculating and searching student performance."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Iterable

from student_grading.config import (
    EXCELLENT_GRADE,
    GOOD_GRADE,
    MAX_GRADE,
    MIN_GRADE,
    PASSING_GRADE,
)
from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord


class PerformanceLevel(StrEnum):
    """Human-readable performance categories on the 100-point scale."""

    EXCELLENT = "відмінно"
    GOOD = "добре"
    SATISFACTORY = "задовільно"
    FAILING = "незадовільно"


@dataclass(frozen=True, slots=True)
class GradeStatistics:
    """Summary values calculated for a collection of student records."""

    record_count: int
    overall_average: float
    minimum_grade: float
    maximum_grade: float
    successful_count: int


def add_student(
    students: list[StudentRecord],
    student: StudentRecord,
) -> None:
    """Add a validated student record to the current collection."""

    students.append(student)


def calculate_average(student: StudentRecord) -> float:
    """Calculate a student's average grade."""

    return student.average_grade


def find_min_max_grades(student: StudentRecord) -> tuple[float, float]:
    """Return the student's minimum and maximum grades."""

    return student.minimum_grade, student.maximum_grade


def determine_performance(student: StudentRecord) -> PerformanceLevel:
    """Classify performance using configured 100-point scale boundaries."""

    average = calculate_average(student)
    if average >= EXCELLENT_GRADE:
        return PerformanceLevel.EXCELLENT
    if average >= GOOD_GRADE:
        return PerformanceLevel.GOOD
    if average >= PASSING_GRADE:
        return PerformanceLevel.SATISFACTORY
    return PerformanceLevel.FAILING


def is_successful(student: StudentRecord) -> bool:
    """Return whether the student's average reaches the passing grade."""

    return calculate_average(student) >= PASSING_GRADE


def sort_students(
    students: Iterable[StudentRecord],
    *,
    descending: bool = True,
) -> list[StudentRecord]:
    """Return records sorted by average, then full name and subject."""

    return sorted(
        students,
        key=lambda student: (
            student.average_grade,
            student.full_name.casefold(),
            student.subject.casefold(),
        ),
        reverse=descending,
    )


def find_students_above_average(
    students: Iterable[StudentRecord],
    threshold: float,
    *,
    subject: str | None = None,
) -> list[StudentRecord]:
    """Find students whose average is strictly above the given threshold."""

    normalized_threshold = _validate_threshold(threshold)
    normalized_subject = subject.strip().casefold() if subject else None

    return [
        student
        for student in students
        if student.average_grade > normalized_threshold
        and (
            normalized_subject is None
            or student.subject.casefold() == normalized_subject
        )
    ]


def search_students(
    students: Iterable[StudentRecord],
    *,
    name_query: str | None = None,
    subject: str | None = None,
    group: str | None = None,
    minimum_average: float | None = None,
) -> list[StudentRecord]:
    """Search by any combination of name, subject, group, and minimum average."""

    normalized_name = name_query.strip().casefold() if name_query else None
    normalized_subject = subject.strip().casefold() if subject else None
    normalized_group = group.strip().casefold() if group else None
    normalized_minimum = (
        _validate_threshold(minimum_average)
        if minimum_average is not None
        else None
    )

    return [
        student
        for student in students
        if (normalized_name is None or normalized_name in student.full_name.casefold())
        and (
            normalized_subject is None
            or student.subject.casefold() == normalized_subject
        )
        and (normalized_group is None or student.group.casefold() == normalized_group)
        and (
            normalized_minimum is None
            or student.average_grade >= normalized_minimum
        )
    ]


def calculate_statistics(students: Iterable[StudentRecord]) -> GradeStatistics:
    """Calculate aggregate statistics for all supplied student records."""

    records = list(students)
    if not records:
        raise GradeValidationError("Statistics require at least one student record.")

    all_grades = [grade for student in records for grade in student.grades]
    return GradeStatistics(
        record_count=len(records),
        overall_average=sum(all_grades) / len(all_grades),
        minimum_grade=min(all_grades),
        maximum_grade=max(all_grades),
        successful_count=sum(is_successful(student) for student in records),
    )


def _validate_threshold(value: float) -> float:
    try:
        threshold = float(value)
    except (TypeError, ValueError) as error:
        raise GradeValidationError("The average threshold must be numeric.") from error

    if not isfinite(threshold) or not MIN_GRADE <= threshold <= MAX_GRADE:
        raise GradeValidationError(
            f"The average threshold must be from {MIN_GRADE:g} to {MAX_GRADE:g}."
        )
    return threshold
