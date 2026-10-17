from collections.abc import Iterator

import pytest

from student_grading.exceptions import GradeValidationError
from student_grading.main import (
    main,
    parse_grades,
    print_students,
    run_demo,
    run_menu,
)
from student_grading.models import StudentRecord


def test_parse_grades() -> None:
    assert parse_grades("90, 80.5,70") == (90.0, 80.5, 70.0)


@pytest.mark.parametrize("raw_value", ["", "90,", "90,x"])
def test_parse_grades_rejects_invalid_input(raw_value: str) -> None:
    with pytest.raises(GradeValidationError):
        parse_grades(raw_value)


def test_demo_contains_required_results(capsys: pytest.CaptureFixture[str]) -> None:
    run_demo(80)
    output = capsys.readouterr().out

    assert "РЕЙТИНГ ЗА СЕРЕДНІМ БАЛОМ" in output
    assert "СЕРЕДНІЙ БАЛ ВИЩЕ 80" in output
    assert "Мінімальна оцінка" in output
    assert "Максимальна оцінка" in output
    assert "Успішних студентів" in output
    assert "СТРУКТУРИ ДАНИХ І ФУНКЦІОНАЛЬНА ДЕКОМПОЗИЦІЯ" in output
    assert "Пошук у dict-index за ID=3" in output


def test_main_rejects_invalid_threshold() -> None:
    with pytest.raises(SystemExit, match="Помилка"):
        main(["--threshold", "101"])


def test_print_students_handles_empty_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_students([], title="ПОРОЖНІЙ РЕЗУЛЬТАТ")

    assert "Записів не знайдено" in capsys.readouterr().out


def test_menu_covers_all_commands(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    answers: Iterator[str] = iter(
        [
            "2",
            "Тестовий Студент",
            "Python",
            "ФеП-32",
            "80, 90",
            "1",
            "3",
            "4",
            "80",
            "5",
            "тест",
            "Python",
            "ФеП-32",
            "70",
            "6",
            "9",
            "0",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    run_menu([])
    output = capsys.readouterr().out

    assert "Запис додано" in output
    assert "Тестовий Студент" in output
    assert "РЕЙТИНГ" in output
    assert "СЕРЕДНІЙ БАЛ ВИЩЕ 80" in output
    assert "РЕЗУЛЬТАТ ПОШУКУ" in output
    assert "Загальний середній бал: 85.00" in output
    assert "Невідома команда" in output
    assert "Роботу завершено" in output


@pytest.mark.parametrize(
    "answers",
    [
        ["2", "", "Python", "ФеП-32", "80", "0"],
        ["4", "not-a-number", "0"],
        ["5", "", "", "", "not-a-number", "0"],
    ],
)
def test_menu_reports_validation_errors(
    answers: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    responses = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))

    run_menu([StudentRecord("Анна Коваль", "Python", [90])])

    assert "Помилка введення" in capsys.readouterr().out


def test_main_routes_to_demo(capsys: pytest.CaptureFixture[str]) -> None:
    main(["--threshold", "90"])

    assert "СЕРЕДНІЙ БАЛ ВИЩЕ 90" in capsys.readouterr().out


def test_main_routes_to_interactive_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_run_menu() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("student_grading.main.run_menu", fake_run_menu)

    main(["--interactive"])

    assert called


def test_main_routes_to_benchmark(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("student_grading.main.run_benchmarks", lambda: [])

    main(["--benchmark"])

    assert "BENCHMARK" in capsys.readouterr().out


def test_main_exports_summary(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "summary.json"

    main(["--export-summary", str(output)])

    assert output.exists()
    assert "експортовано" in capsys.readouterr().out
