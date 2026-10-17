"""Reproducible list-versus-dict lookup benchmark for laboratory work 2."""

from __future__ import annotations

from dataclasses import dataclass
from timeit import repeat


BenchmarkRecord = tuple[int, str]
DEFAULT_SIZES: tuple[int, ...] = (1_000, 10_000, 100_000)


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """Average lookup durations for one input size."""

    record_count: int
    list_search_seconds: float
    dict_search_seconds: float

    @property
    def speedup(self) -> float:
        """Return how many times the indexed lookup is faster."""

        return self.list_search_seconds / self.dict_search_seconds


def build_benchmark_records(size: int) -> list[BenchmarkRecord]:
    """Create structured tuple records with unique numeric IDs."""

    if size <= 0:
        raise ValueError("Benchmark size must be positive.")
    return [(student_id, f"Студент {student_id}") for student_id in range(size)]


def find_record_linear(
    records: list[BenchmarkRecord],
    student_id: int,
) -> BenchmarkRecord | None:
    """Find a tuple record by ID with O(n) list traversal."""

    for record in records:
        if record[0] == student_id:
            return record
    return None


def benchmark_search(size: int, *, number: int = 25) -> BenchmarkResult:
    """Measure worst-case list lookup and average O(1) dict lookup."""

    if number <= 0:
        raise ValueError("Benchmark iteration count must be positive.")
    records = build_benchmark_records(size)
    index = {record[0]: record for record in records}
    target = size - 1

    list_total = min(
        repeat(
            lambda: find_record_linear(records, target),
            repeat=3,
            number=number,
        )
    )
    dict_total = min(
        repeat(
            lambda: index.get(target),
            repeat=3,
            number=number,
        )
    )
    return BenchmarkResult(
        record_count=size,
        list_search_seconds=list_total / number,
        dict_search_seconds=dict_total / number,
    )


def run_benchmarks(
    sizes: tuple[int, ...] = DEFAULT_SIZES,
    *,
    number: int = 25,
) -> list[BenchmarkResult]:
    """Run the required experiment for all configured data sizes."""

    return [benchmark_search(size, number=number) for size in sizes]


def format_benchmark_table(results: list[BenchmarkResult]) -> str:
    """Format benchmark values as a readable fixed-width table."""

    lines = [
        f"{'Records':>10} {'list, µs':>14} "
        f"{'dict, µs':>14} {'Прискорення':>14}",
        "-" * 56,
    ]
    lines.extend(
        f"{result.record_count:10,d} "
        f"{result.list_search_seconds * 1_000_000:14.3f} "
        f"{result.dict_search_seconds * 1_000_000:14.3f} "
        f"{result.speedup:13.1f}x"
        for result in results
    )
    return "\n".join(lines)
