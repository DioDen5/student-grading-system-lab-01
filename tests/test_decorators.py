from student_grading.decorators import (
    clear_operation_history,
    recent_operations,
    track_operation,
)


def test_parameterized_decorator_preserves_function_and_records_call() -> None:
    clear_operation_history()

    @track_operation("addition")
    def add(*values: int, offset: int = 0) -> int:
        """Add values for the decorator test."""

        return sum(values) + offset

    assert add(1, 2, 3, offset=4) == 10
    assert add.__name__ == "add"
    assert add.__doc__ == "Add values for the decorator test."
    assert recent_operations()[0][0] == "addition"


def test_history_is_bounded_and_can_use_default_label() -> None:
    clear_operation_history()

    @track_operation()
    def identity(value: int) -> int:
        return value

    for value in range(12):
        assert identity(value) == value

    history = recent_operations()
    assert len(history) == 10
    assert all(name == "identity" for name, _elapsed in history)
