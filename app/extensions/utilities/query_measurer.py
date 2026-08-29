from contextlib import AbstractContextManager, ContextDecorator
from logging import getLogger
from timeit import timeit
from types import TracebackType
from typing import Any, Callable, Literal, NamedTuple, Optional, cast, overload
from django.conf import settings
from django.db import connection


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
        return self._queries

    @property
    def query_count(self) -> int:
        return len(self.queries)

    @property
    def query_time(self) -> float:
        return sum(q.time_ms for q in self.queries)

    @property
    def slowest_query(self) -> QueryData:
        try:
            return max(self.queries, key=lambda x: x.time_ms)
        except ValueError as ve:
            raise ValueError("No queries present!") from ve

    def get_filtered_queries(self, statement: StatementType) -> list[QueryData]:
        return [q for q in self.queries if q.statement == statement]

    def get_filtered_queries_count(self, statement: StatementType) -> int:
        return len(self.get_filtered_queries(statement))

    def get_filtered_queries_time(self, statement: StatementType) -> float:
        return sum(q.time_ms for q in self.get_filtered_queries(statement))


class QueryMeasurer(ContextDecorator):
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

    def _execute_wrapper(
        self,
        execute: Callable[[str, Any, bool, dict[str, Any]], Any],
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> None:
        execution_callable = lambda: execute(sql, params, many, context)
        duration_seconds = timeit(execution_callable, number=1)
        data = QueryData(sql, cast(StatementType, sql.split(maxsplit=1)[0]), duration_seconds * 1000)
        self.ctx._queries.append(data)

    def __enter__(self) -> QueryMeasurerContext:
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
def query_measurer[F: Callable[..., Any]](func: F) -> F: ...


# Decorator or context-manager with parameters
@overload
def query_measurer(*, handler: Optional[Callable[[QueryMeasurerContext], None]] = ...) -> QueryMeasurer: ...


# Implementation
def query_measurer[F: Callable[..., Any]](
    func: Optional[F] = None,
    *,
    handler: Optional[Callable[[QueryMeasurerContext], None]] = None,
) -> F | Callable[[F], F] | QueryMeasurer:
    """
    Utility to measure queries in code blocks; it can be used as a decorator or as a context manager. Check the
    QueryMeasurerContext class to see all the collected data.

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
    ```
    """
    if callable(func):
        return QueryMeasurer(handler=handler or default_handler)(func)
    else:
        return QueryMeasurer(handler)
