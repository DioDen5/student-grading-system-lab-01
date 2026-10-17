"""Collection-oriented processing functions for laboratory work 2."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from typing import TypeVar

from student_grading.decorators import track_operation
from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord


T = TypeVar("T")
K = TypeVar("K")


def unique_subjects(students: Iterable[StudentRecord]) -> set[str]:
    """Build a set of unique subjects using a set comprehension."""

    return {student.subject for student in students}


@track_operation("group_by_subject")
def group_by_subject(
    students: Iterable[StudentRecord],
) -> dict[str, list[StudentRecord]]:
    """Group records by subject with defaultdict."""

    grouped: defaultdict[str, list[StudentRecord]] = defaultdict(list)
    for student in students:
        grouped[student.subject].append(student)
    return dict(grouped)


def count_subjects(students: Iterable[StudentRecord]) -> Counter[str]:
    """Count student records by subject with Counter and a generator."""

    return Counter(student.subject for student in students)


def index_students_by_id(
    students: Iterable[StudentRecord],
) -> dict[int, StudentRecord]:
    """Create an O(1)-average lookup index using a dict comprehension."""

    records = list(students)
    missing_ids = [
        student.full_name
        for student in records
        if student.student_id is None
    ]
    if missing_ids:
        raise GradeValidationError(
            "Every indexed student must have an ID. Missing: "
            + ", ".join(missing_ids)
        )

    index = {
        student.student_id: student
        for student in records
        if student.student_id is not None
    }
    if len(index) != len(records):
        raise GradeValidationError("Student IDs must be unique.")
    return index


def index_students_by_name(
    students: Iterable[StudentRecord],
) -> dict[str, StudentRecord]:
    """Create a normalized full-name index."""

    return {student.full_name.casefold(): student for student in students}


def find_student_linear(
    students: Iterable[StudentRecord],
    student_id: int,
) -> StudentRecord | None:
    """Find a student by ID with O(n) linear search."""

    for student in students:
        if student.student_id == student_id:
            return student
    return None


def filter_items(items: Iterable[T], predicate: Callable[[T], bool]) -> list[T]:
    """Apply a caller-supplied predicate using a list comprehension."""

    return [item for item in items if predicate(item)]


def sort_items(
    items: Iterable[T],
    *,
    key: Callable[[T], K],
    reverse: bool = False,
) -> list[T]:
    """Sort arbitrary records with a higher-order key function."""

    return sorted(items, key=key, reverse=reverse)


def group_by_subject_and_group(
    students: Iterable[StudentRecord],
) -> dict[str, dict[str, list[StudentRecord]]]:
    """Build an advanced nested grouping: subject -> group -> students."""

    nested: defaultdict[
        str, defaultdict[str, list[StudentRecord]]
    ] = defaultdict(lambda: defaultdict(list))
    for student in students:
        nested[student.subject][student.group].append(student)
    return {
        subject: dict(group_records)
        for subject, group_records in nested.items()
    }


def process_pipeline(
    items: Iterable[T],
    *operations: Callable[[list[T]], Iterable[T]],
) -> list[T]:
    """Apply any number of processing operations in sequence."""

    result = list(items)
    for operation in operations:
        result = list(operation(result))
    return result
