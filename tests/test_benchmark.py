import pytest

from student_grading.benchmark import (
    BenchmarkResult,
    benchmark_search,
    build_benchmark_records,
    find_record_linear,
    format_benchmark_table,
    run_benchmarks,
)


def test_build_and_find_benchmark_records() -> None:
    records = build_benchmark_records(5)

    assert records[0] == (0, "Студент 0")
    assert find_record_linear(records, 4) == (4, "Студент 4")
    assert find_record_linear(records, 99) is None


@pytest.mark.parametrize("size", [0, -1])
def test_invalid_benchmark_size(size: int) -> None:
    with pytest.raises(ValueError):
        build_benchmark_records(size)


def test_benchmark_and_formatting() -> None:
    result = benchmark_search(100, number=2)
    table = format_benchmark_table([result])

    assert result.record_count == 100
    assert result.list_search_seconds > 0
    assert result.dict_search_seconds > 0
    assert result.speedup > 0
    assert "Records" in table
    assert "100" in table


def test_invalid_iteration_count() -> None:
    with pytest.raises(ValueError):
        benchmark_search(10, number=0)


def test_run_benchmarks_uses_requested_sizes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "student_grading.benchmark.benchmark_search",
        lambda size, number: BenchmarkResult(size, 1.0, 0.5),
    )

    results = run_benchmarks((10, 20), number=1)

    assert [result.record_count for result in results] == [10, 20]
