"""Data models for student assessment records."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

from student_grading.config import MAX_GRADE, MIN_GRADE
from student_grading.exceptions import GradeValidationError


@dataclass(frozen=True, slots=True)
class StudentRecord:
    """Grades earned by one student in one academic subject."""

    full_name: str
    subject: str
    grades: tuple[float, ...]
    group: str
    student_id: int | None

    def __init__(
        self,
        full_name: str,
        subject: str,
        grades: Iterable[float],
        group: str = "ФеП-32",
        student_id: int | None = None,
    ) -> None:
        normalized_name = full_name.strip()
        normalized_subject = subject.strip()
        normalized_group = group.strip()

        if not normalized_name:
            raise GradeValidationError("Student full name must not be empty.")
        if not normalized_subject:
            raise GradeValidationError("Subject must not be empty.")
        if not normalized_group:
            raise GradeValidationError("Student group must not be empty.")
        if student_id is not None and (
            isinstance(student_id, bool)
            or not isinstance(student_id, int)
            or student_id <= 0
        ):
            raise GradeValidationError("Student ID must be a positive integer.")

        try:
            normalized_grades = tuple(float(grade) for grade in grades)
        except (TypeError, ValueError) as error:
            raise GradeValidationError("Every grade must be a number.") from error

        if not normalized_grades:
            raise GradeValidationError("At least one grade is required.")

        invalid_grades = [
            grade
            for grade in normalized_grades
            if not isfinite(grade) or not MIN_GRADE <= grade <= MAX_GRADE
        ]
        if invalid_grades:
            raise GradeValidationError(
                f"Grades must be finite numbers from {MIN_GRADE:g} "
                f"to {MAX_GRADE:g}. Invalid values: {invalid_grades}"
            )

        object.__setattr__(self, "full_name", normalized_name)
        object.__setattr__(self, "subject", normalized_subject)
        object.__setattr__(self, "grades", normalized_grades)
        object.__setattr__(self, "group", normalized_group)
        object.__setattr__(self, "student_id", student_id)

    @property
    def average_grade(self) -> float:
        """Return the arithmetic mean of all grades."""

        return sum(self.grades) / len(self.grades)

    @property
    def minimum_grade(self) -> float:
        """Return the lowest grade."""

        return min(self.grades)

    @property
    def maximum_grade(self) -> float:
        """Return the highest grade."""

        return max(self.grades)


# A concise public name is convenient for imports and automated checks.
Student = StudentRecord
