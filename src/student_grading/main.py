"""Console entry point for the student grading system."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from student_grading.analytics import (
    aggregate_by_subject,
    create_average_filter,
    export_summary,
    grade_distribution,
)
from student_grading.benchmark import format_benchmark_table, run_benchmarks
from student_grading.config import DEFAULT_SEARCH_THRESHOLD
from student_grading.data import load_demo_students
from student_grading.decorators import recent_operations
from student_grading.exceptions import GradeValidationError
from student_grading.models import StudentRecord
from student_grading.processors import (
    count_subjects,
    filter_items,
    group_by_subject,
    group_by_subject_and_group,
    index_students_by_id,
    process_pipeline,
    sort_items,
    unique_subjects,
)
from student_grading.services import (
    add_student,
    calculate_statistics,
    determine_performance,
    find_students_above_average,
    search_students,
    sort_students,
)


def create_demo_students() -> list[StudentRecord]:
    """Create deterministic data for demonstration and manual checks."""

    return load_demo_students()


def parse_grades(raw_value: str) -> tuple[float, ...]:
    """Parse comma-separated grades and reject malformed input."""

    values = [item.strip() for item in raw_value.split(",")]
    if not values or any(not item for item in values):
        raise GradeValidationError(
            "Enter at least one grade; separate several grades with commas."
        )
    try:
        return tuple(float(item) for item in values)
    except ValueError as error:
        raise GradeValidationError("Every grade must be a number.") from error


def print_students(
    students: Sequence[StudentRecord],
    *,
    title: str = "СТУДЕНТИ",
) -> None:
    """Print student records as a readable console table."""

    print(f"\n{title}")
    print(
        f"{'ID':>3} {'ПІБ':22} {'Група':8} {'Дисципліна':14} "
        f"{'Сер.':>6} {'Мін.':>6} {'Макс.':>6} Статус"
    )
    print("-" * 97)
    if not students:
        print("Записів не знайдено.")
        return

    for student in students:
        print(
            f"{student.student_id or '-':>3} "
            f"{student.full_name:22} "
            f"{student.group:8} "
            f"{student.subject:14} "
            f"{student.average_grade:6.2f} "
            f"{student.minimum_grade:6.2f} "
            f"{student.maximum_grade:6.2f} "
            f"{determine_performance(student)}"
        )


def run_demo(threshold: float = DEFAULT_SEARCH_THRESHOLD) -> None:
    """Run a non-interactive demonstration of every required operation."""

    students = create_demo_students()
    print_students(students, title="УСІ ЗАПИСИ")
    print_students(
        sort_students(students),
        title="РЕЙТИНГ ЗА СЕРЕДНІМ БАЛОМ",
    )

    above_threshold = find_students_above_average(students, threshold)
    print_students(
        above_threshold,
        title=f"СЕРЕДНІЙ БАЛ ВИЩЕ {threshold:g}",
    )

    statistics = calculate_statistics(students)
    print("\nЗАГАЛЬНА СТАТИСТИКА")
    print(f"Кількість записів: {statistics.record_count}")
    print(
        "Середній бал за всіма оцінками: "
        f"{statistics.overall_average:.2f}"
    )
    print(f"Мінімальна оцінка: {statistics.minimum_grade:.2f}")
    print(f"Максимальна оцінка: {statistics.maximum_grade:.2f}")
    print(f"Успішних студентів: {statistics.successful_count}")

    grouped = group_by_subject(students)
    nested = group_by_subject_and_group(students)
    subject_statistics = aggregate_by_subject(students)
    student_index = index_students_by_id(students)
    minimum_filter = create_average_filter(threshold)
    pipeline_result = process_pipeline(
        students,
        lambda records: filter_items(records, minimum_filter),
        lambda records: sort_items(
            records,
            key=lambda student: student.average_grade,
            reverse=True,
        ),
    )

    print("\nСТРУКТУРИ ДАНИХ І ФУНКЦІОНАЛЬНА ДЕКОМПОЗИЦІЯ")
    print(
        "Унікальні дисципліни (set): "
        f"{sorted(unique_subjects(students))}"
    )
    print(f"Counter дисциплін: {dict(count_subjects(students))}")
    print(f"Counter оцінок: {dict(grade_distribution(students).most_common(5))}")
    group_sizes = {key: len(value) for key, value in grouped.items()}
    print(f"Групування за дисциплінами: {group_sizes}")
    print(
        "Вкладене групування: "
        + str(
            {
                subject: {
                    group: len(records)
                    for group, records in groups.items()
                }
                for subject, groups in nested.items()
            }
        )
    )
    print(f"Пошук у dict-index за ID=3: {student_index[3].full_name}")
    print(
        "Агрегація за дисциплінами: "
        + str(
            {
                subject: round(values.average_grade, 2)
                for subject, values in subject_statistics.items()
            }
        )
    )
    print(
        "Pipeline (closure + filter + lambda sort): "
        + ", ".join(student.full_name for student in pipeline_result)
    )
    print(
        "Історія операцій (deque): "
        + ", ".join(name for name, _elapsed in recent_operations())
    )


def print_menu() -> None:
    """Display available interactive commands."""

    print("\n1. Показати всі записи")
    print("2. Додати студента")
    print("3. Показати рейтинг")
    print("4. Знайти середній бал вище заданого")
    print("5. Пошук за кількома критеріями")
    print("6. Показати статистику")
    print("0. Завершити роботу")


def run_menu(students: list[StudentRecord] | None = None) -> None:
    """Run the menu-driven interface with validated keyboard input."""

    records = create_demo_students() if students is None else students
    actions = {
        "1": lambda: print_students(records, title="УСІ ЗАПИСИ"),
        "2": lambda: _add_student_from_input(records),
        "3": lambda: print_students(
            sort_students(records), title="РЕЙТИНГ ЗА СЕРЕДНІМ БАЛОМ"
        ),
        "4": lambda: _find_above_threshold_from_input(records),
        "5": lambda: _search_from_input(records),
        "6": lambda: _print_statistics(records),
    }

    while True:
        print_menu()
        command = input("Оберіть команду: ").strip()
        if command == "0":
            print("Роботу завершено.")
            return

        action = actions.get(command)
        if action is None:
            print("Невідома команда. Введіть число від 0 до 6.")
            continue

        try:
            action()
        except GradeValidationError as error:
            print(f"Помилка введення: {error}")


def _add_student_from_input(students: list[StudentRecord]) -> None:
    full_name = input("ПІБ: ").strip()
    subject = input("Дисципліна: ").strip()
    group = input("Група: ").strip()
    grades = parse_grades(input("Оцінки через кому: "))
    next_id = max(
        (student.student_id or 0 for student in students),
        default=0,
    ) + 1
    add_student(
        students,
        StudentRecord(
            full_name,
            subject,
            grades,
            group=group,
            student_id=next_id,
        ),
    )
    print("Запис додано.")


def _find_above_threshold_from_input(students: list[StudentRecord]) -> None:
    raw_threshold = input("Пороговий середній бал: ").strip()
    try:
        threshold = float(raw_threshold)
    except ValueError as error:
        raise GradeValidationError("The average threshold must be numeric.") from error
    print_students(
        find_students_above_average(students, threshold),
        title=f"СЕРЕДНІЙ БАЛ ВИЩЕ {threshold:g}",
    )


def _search_from_input(students: list[StudentRecord]) -> None:
    name_query = input("Частина ПІБ або Enter: ").strip() or None
    subject = input("Дисципліна або Enter: ").strip() or None
    group = input("Група або Enter: ").strip() or None
    raw_average = input("Мінімальний середній бал або Enter: ").strip()
    minimum_average: float | None = None
    if raw_average:
        try:
            minimum_average = float(raw_average)
        except ValueError as error:
            raise GradeValidationError(
                "The average threshold must be numeric."
            ) from error

    print_students(
        search_students(
            students,
            name_query=name_query,
            subject=subject,
            group=group,
            minimum_average=minimum_average,
        ),
        title="РЕЗУЛЬТАТ ПОШУКУ",
    )


def _print_statistics(students: list[StudentRecord]) -> None:
    statistics = calculate_statistics(students)
    print(f"Записів: {statistics.record_count}")
    print(f"Загальний середній бал: {statistics.overall_average:.2f}")
    print(f"Мінімум: {statistics.minimum_grade:.2f}")
    print(f"Максимум: {statistics.maximum_grade:.2f}")
    print(f"Успішних: {statistics.successful_count}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(description="Система оцінювання студентів")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="відкрити інтерактивне меню",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="порівняти пошук у list і dict для 1 000-100 000 записів",
    )
    parser.add_argument(
        "--export-summary",
        type=Path,
        metavar="PATH",
        help="експортувати JSON-підсумок демонстраційних даних",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_SEARCH_THRESHOLD,
        help="поріг середнього бала для демонстраційного пошуку",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Run either the deterministic demo or the interactive interface."""

    arguments = build_parser().parse_args(argv)
    if arguments.interactive:
        run_menu()
        return

    if arguments.benchmark:
        print("BENCHMARK: ПОШУК У LIST ПРОТИ DICT")
        print(format_benchmark_table(run_benchmarks()))
        return

    try:
        run_demo(arguments.threshold)
        if arguments.export_summary is not None:
            output = export_summary(
                arguments.export_summary,
                create_demo_students(),
            )
            print(f"Підсумок експортовано: {output}")
    except GradeValidationError as error:
        raise SystemExit(f"Помилка: {error}") from error


if __name__ == "__main__":  # pragma: no cover - exercised by module execution
    main()
