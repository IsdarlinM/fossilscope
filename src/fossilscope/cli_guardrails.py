from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

import click
import typer
from pydantic import ValidationError
from sric.errors import safe_exception_message

F = TypeVar("F", bound=Callable[..., Any])

PREDICTABLE_OPERATION_ERRORS = (
    FileNotFoundError,
    IsADirectoryError,
    KeyError,
    NotADirectoryError,
    OSError,
    PermissionError,
    TypeError,
    ValidationError,
    ValueError,
)


def _guard_callback(callback: F) -> F:
    if getattr(callback, "_fossilscope_guarded", False):
        return callback

    @wraps(callback)
    def guarded(*args: Any, **kwargs: Any) -> Any:
        try:
            return callback(*args, **kwargs)
        except (click.ClickException, click.exceptions.Exit):
            raise
        except PREDICTABLE_OPERATION_ERRORS as exc:
            typer.echo(
                f"Operation rejected: {type(exc).__name__}: {safe_exception_message(exc)}",
                err=True,
            )
            raise typer.Exit(2) from None
        except Exception as exc:
            typer.echo(
                f"Operation failed safely: {type(exc).__name__}: {safe_exception_message(exc)}",
                err=True,
            )
            raise typer.Exit(1) from None

    setattr(guarded, "_fossilscope_guarded", True)
    return cast(F, guarded)


def install_cli_callback_guardrails(app: typer.Typer) -> None:
    """Wrap every registered command callback after the complete CLI is assembled.

    Click/Typer usage exceptions keep their native behavior. Expected file/value/schema
    problems become controlled exit 2 responses. Any other callback exception is
    redacted and converted to a controlled exit 1 response. The Web fixed runner invokes
    the same Typer app, so this is shared by terminal and Web execution paths.
    """

    for command in app.registered_commands:
        callback = command.callback
        if callback is not None:
            command.callback = _guard_callback(callback)
