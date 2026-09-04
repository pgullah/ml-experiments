
import logging as stdlib_logging
from functools import wraps
from time import perf_counter
from typing import Callable, ParamSpec, TypeVar, overload


P = ParamSpec("P")
R = TypeVar("R")


@overload
def logging(method: Callable[P, R], *, level: int = stdlib_logging.INFO) -> Callable[P, R]: ...


@overload
def logging(*, level: int = stdlib_logging.INFO) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def logging(method=None, *, level: int = stdlib_logging.INFO):
    """Log a callable's lifecycle, using INFO unless ``level`` is overridden."""
    def decorate(target):
        method_logger = stdlib_logging.getLogger(target.__module__)

        @wraps(target)
        def wrapper(*args, **kwargs):
            method_name = target.__qualname__
            start_time = perf_counter()
            method_logger.log(level, "Entering %s", method_name)

            try:
                result = target(*args, **kwargs)
            except Exception:
                method_logger.exception(
                    "Failed %s after %.2f ms",
                    method_name,
                    (perf_counter() - start_time) * 1_000,
                )
                raise

            method_logger.log(
                level,
                "Completed %s in %.2f ms",
                method_name,
                (perf_counter() - start_time) * 1_000,
            )
            return result

        return wrapper

    if method is None:
        return decorate
    return decorate(method)


def lazy_init(scope, variable_name, init_func):
    if not hasattr(scope, variable_name):
        setattr(scope, variable_name, init_func())

    return getattr(scope, variable_name)
