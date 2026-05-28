import click


def log(message: str) -> None:
    click.echo(message)


def success(message: str, *, bold: bool = True) -> None:
    click.echo(click.style(message, fg="green", bold=bold))


def warning(message: str, *, bold: bool = True) -> None:
    click.echo(click.style(message, fg="yellow", bold=bold))


def error(message: str, *, bold: bool = True) -> None:
    click.echo(click.style(message, fg="red", bold=bold), err=True)
