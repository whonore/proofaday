import os
import signal
import sys
from pathlib import Path
from typing import Any, Callable, TypeVar

import click

import proofaday.constants as consts
from proofaday.cli_util import ClickPath
from proofaday.daemon import ServerError, spawn
from proofaday.status import Status

pass_status = click.make_pass_decorator(Status)


class ServerInvoker(click.Group):
    def invoke(self, ctx: click.core.Context) -> None:
        try:
            super().invoke(ctx)
        except ServerError as e:
            sys.exit(str(e))


F = TypeVar("F", bound=Callable[..., Any])


def start_options(f: F) -> F:
    for opt in (
        click.option(
            "-p",
            "--port",
            help="Port for the daemon to listen on.",
            default=0,
        ),
        click.option(
            "-f",
            "--force/--no-force",
            help="Force the daemon to start even if one is already running.",
            default=False,
        ),
        click.option(
            "-l",
            "--line-limit",
            help="Maximum number of lines in a proof to accept. Use 0 for no limit.",
            type=click.IntRange(min=0),
            default=0,
            show_default=True,
        ),
        click.option(
            "-n",
            "--num-prefetch-proofs",
            "nprefetch",
            help="Number of proofs to prefetch.",
            type=click.IntRange(min=1),
            default=consts.NPREFETCH,
            show_default=True,
        ),
        click.option(
            "-d",
            "--debug",
            help="Enable debugging output.",
            count=True,
        ),
        click.option(
            "--log-path",
            help="Directory to place the debug log.",
            type=ClickPath(exists=False, file_okay=False),
            default=consts.LOG_PATH,
        ),
    ):
        f = opt(f)
    return f


@click.group(cls=ServerInvoker, help="A daemon to fetch proofs.")
@click.option(
    "-q",
    "--quiet/--no-quiet",
    help="Disable output.",
    default=False,
)
@click.option(
    "--status-path",
    help="Directory to place the status file.",
    type=ClickPath(exists=False, file_okay=False),
    default=consts.DATA_PATH,
)
@click.pass_context
def main(ctx: click.core.Context, quiet: bool, status_path: Path) -> None:
    ctx.obj = Status(status_path)
    if quiet:
        sys.stdout = sys.stderr = open(os.devnull, "w")


@main.command(help="Start the daemon.")
@start_options
@pass_status
def start(status: Status, force: bool, **kwargs: Any) -> None:
    if status.read() is not None:
        if not force:
            raise ServerError("Daemon already started.")
        elif not status.remove():
            raise ServerError("Failed to remove status file.")
    spawn(status=status, **kwargs)


@main.command(help="Stop the daemon.")
@pass_status
def stop(status: Status) -> None:
    data = status.read()
    if data is None:
        raise ServerError("Daemon not running.")
    try:
        os.kill(data["pid"], signal.SIGTERM)
    except ProcessLookupError:
        raise ServerError("Daemon not running.")
    finally:
        if not status.wait(exist=False):
            raise ServerError("Failed to stop daemon.")


@main.command(help="Restart the daemon.")
@start_options
@pass_status
@click.pass_context
def restart(ctx: click.core.Context, status: Status, **kwargs: Any) -> None:
    ctx.invoke(stop)
    ctx.forward(start)


@main.command(help="Check the status of the daemon.")
@click.option(
    "-w",
    "--wait/--no-wait",
    help="Block until the status is available.",
    default=False,
)
@pass_status
def status(status: Status, wait: bool) -> None:
    try:
        if wait:
            status.wait(exist=True, timeout=None)
        click.echo(status)
    except ValueError:
        raise ServerError("Failed to read status file.")


if __name__ == "__main__":
    main()
