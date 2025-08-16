from typing import Any, Callable
import click


def confirm_opt[F: Callable[..., Any]](func: F) -> F:
    return click.option("-y", "--yes", is_flag=True, default=False, help="Confirm ALL choices as 'yes'.")(func)
