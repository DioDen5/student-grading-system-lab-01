"""Reusable decorators and bounded operation history."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")
Operation = tuple[str, float]

_OPERATION_HISTORY: deque[Operation] = deque(maxlen=10)


def track_operation(
    label: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Create a parameterized timing decorator and remember recent calls."""

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        operation_name = label or function.__name__

        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                _OPERATION_HISTORY.append(
                    (operation_name, perf_counter() - started)
                )

        return wrapper

    return decorator


def recent_operations() -> tuple[Operation, ...]:
    """Return an immutable snapshot of the bounded deque history."""

    return tuple(_OPERATION_HISTORY)


def clear_operation_history() -> None:
    """Clear recorded operations, primarily for deterministic tests."""

    _OPERATION_HISTORY.clear()
