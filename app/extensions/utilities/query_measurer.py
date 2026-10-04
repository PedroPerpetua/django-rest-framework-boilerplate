from contextlib import AbstractContextManager
from functools import wraps
from logging import getLogger
from timeit import timeit
from types import TracebackType
from typing import Any, Callable, Literal, NamedTuple, Optional, cast, overload
from django.conf import settings
from django.db import connection
from django.utils.decorators import classonlymethod
from django.views import View


logger = getLogger()


StatementType = Literal["SELECT", "UPDATE", "DELETE", "INSERT"]


class QueryData(NamedTuple):
    """Simple representation of a query to be stored by the QueryMeasurerContext."""

    raw_sql: str
    statement: StatementType
    time_ms: float


class QueryMeasurerContext:
    """Data structure used by the QueryMeasurer, that stores the queries that were made."""

    def __init__(self) -> None:
        self._queries: list[QueryData] = []

    @property
    def queries(self) -> list[QueryData]:
        """List of all queries measured."""
        return self._queries

    @property
    def query_count(self) -> int:
        """Count of how many queries where measured."""
        return len(self.queries)

    @property
    def query_time(self) -> float:
        """Total time summed of all queries measured."""
        return sum(q.time_ms for q in self.queries)

    @property
    def slowest_query(self) -> QueryData:
        """
        Slowest query that was measured.

        If no queries were measured, raises ValueError.
        """
        try:
            return max(self.queries, key=lambda x: x.time_ms)
        except ValueError as ve:
            raise ValueError("No queries present!") from ve

    def get_filtered_queries(self, statement: StatementType) -> list[QueryData]:
        """Returns the queries measured filtered by the given SQL statement."""
        return [q for q in self.queries if q.statement == statement]

    def get_filtered_queries_count(self, statement: StatementType) -> int:
        """Returns the count of all the measured queries filtered by the given SQL statement."""
        return len(self.get_filtered_queries(statement))

    def get_filtered_queries_time(self, statement: StatementType) -> float:
        """Returns the total time summed of all the measured queries filtered by the given SQL statement."""
        return sum(q.time_ms for q in self.get_filtered_queries(statement))


class QueryMeasurer:
    """
    The QueryMeasurer utility.

    This utility should **not** be used directly. Instead, use the `query_measurer` function that will instantiate this
    class and provide it as necessary.
    """

    def __init__(self, handler: Optional[Callable[[QueryMeasurerContext], None]] = None) -> None:
        if not settings.DEBUG:
            logger.warning("Warning! Query measurer should not be used in production; it's merely a debug tool.")
        self.ctx = QueryMeasurerContext()
        self.handler = handler
        self.wrapper: Optional[AbstractContextManager] = None

    @overload
    def __call__[F: Callable[..., Any]](self, FuncOrClass: F, /) -> F: ...

    @overload
    def __call__[C](self, FuncOrClass: type[C], /) -> type[C]: ...

    def __call__[F: Callable[..., Any], C](self, FuncOrClass: F | type[C], /) -> F | type[C]:
        if isinstance(FuncOrClass, type):
            # If we're a class, ensure we're a view
            if not issubclass(FuncOrClass, View):
                raise ValueError("Query measurer can only wrap classes that are Views!")

            #  https://github.com/python/mypy/issues/14458
            class Inner(FuncOrClass):  # type: ignore[valid-type, misc]
                @classonlymethod
                def as_view(cls, **initkwargs: Any) -> Any:
                    # Wrap the returning view function from the `as_view` method.
                    return self(super().as_view(**initkwargs))

            return Inner

        else:
            # We're a function; wrap it
            @wraps(FuncOrClass)
            def inner(*args: Any, **kwargs: Any) -> Any:
                with self:
                    return FuncOrClass(*args, **kwargs)

            return cast(F, inner)

    def _execute_wrapper(
        self,
        execute: Callable[[str, Any, bool, dict[str, Any]], Any],
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> None:
        """Wrapper that will be called by the Django's connection on every query."""
        execution_callable = lambda: execute(sql, params, many, context)
        duration_seconds = timeit(execution_callable, number=1)
        data = QueryData(sql, cast(StatementType, sql.split(maxsplit=1)[0]), duration_seconds * 1000)
        self.ctx._queries.append(data)

    def __enter__(self) -> QueryMeasurerContext:
        self.ctx = QueryMeasurerContext()  # Reset so we get new results on every call
        self.wrapper = connection.execute_wrapper(self._execute_wrapper)
        self.wrapper.__enter__()
        return self.ctx

    def __exit__(self, exc_type: type[Exception], exc: Exception, tb: TracebackType) -> None:
        if self.wrapper is not None:
            self.wrapper.__exit__(exc_type, exc, tb)
        if self.handler:
            self.handler(self.ctx)


def format_query_context(ctx: QueryMeasurerContext, *, start_newline: bool = False) -> str:
    """Auxiliary formatter for the context."""

    def format_query(query: QueryData) -> str:
        time = f"{query.time_ms:.2f}".rjust(6)
        return f"{time} | {query.statement} | {query.raw_sql}"

    message = []
    message.append(f"{'\n' if start_newline else ''}Query Measurer results")
    message.append("---")
    message.append(f"Total Queries: {ctx.query_count}")
    message.append(f"Total Time (ms): {ctx.query_time:.2f}")
    if ctx.query_count > 0:
        message.append(f"Slowest Query: {format_query(ctx.slowest_query)}")
    message.append("---")
    message.extend(format_query(q) for q in ctx.queries)
    return "\n".join(message)


def default_handler(ctx: QueryMeasurerContext) -> None:
    """
    Default handler for the QueryMeasurer, when called as a decorator.

    The default behaviour is to format and log the information gathered at a DEBUG level.
    """
    logger.debug(format_query_context(ctx, start_newline=True))


# Bare decorator
@overload
def query_measurer[F: Callable[..., Any]](funcOrClass: F, /) -> F: ...


# Decorator or context-manager with parameters
@overload
def query_measurer(*, handler: Optional[Callable[[QueryMeasurerContext], None]] = ...) -> QueryMeasurer: ...


# Implementation
def query_measurer[F: Callable[..., Any]](
    funcOrClass: Optional[F] = None,
    /,
    *,
    handler: Optional[Callable[[QueryMeasurerContext], None]] = None,
) -> F | Callable[[F], F] | QueryMeasurer:
    """
    Utility to measure queries in code blocks; it can be used as a decorator (for functions or Views) or as a context
    manager. Check the QueryMeasurerContext class to see all the collected data.

    Note: this is purely a debugging tool, and should be used only in development to test and check performance.

    Example usage as a context manager:
    ```
    with query_measurer() as ctx:
        # Perform some queries
        MyModel.objects.create(...)
    # Check the results
    print(ctx.query_count)
    print(ctx.slowest_query)
    ```

    Example usage as a decorator:
    ```
    # Handler to check the results - if none is provided, results will be logged with level DEBUG
    def handler(ctx: QueryMeasurerContext) -> None:
        # Check the results
        print(ctx.query_count)
        print(ctx.slowest_query)

    @query_measurer(handler=handler)
    def function_to_evaluate() -> None:
        # Perform some queries
        MyModel.objects.create(...)

    # It can also be used to decorate Views
    @query_measurer(handler=handler)
    class MyView(RetrieveAPIView[MyModel]):
        def get_object(self) -> MyModel:
            return MyModel.objects.get(...)
    ```
    """
    if callable(funcOrClass):
        return QueryMeasurer(handler=handler or default_handler)(funcOrClass)
    else:
        return QueryMeasurer(handler)
