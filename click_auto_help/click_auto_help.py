#!/usr/bin/env python3

from typing import IO
from typing import Any

import click


class HelpfulUsageError(click.UsageError):
    """A usage error shown under the whole help of the command it is about:
    its arguments, options and subcommands on the screen beside what went
    wrong, rather than a usage line and a pointer to --help."""

    def show(self, file: IO[Any] | None = None) -> None:
        color = self.ctx.color if self.ctx is not None else None
        if self.ctx is not None:
            click.echo(self.ctx.get_help(), file=file, err=True, color=color)
            click.echo(file=file, err=True)
        click.echo(f"Error: {self.format_message()}", file=file, err=True, color=color)


def helpful(error: click.UsageError, ctx: click.Context) -> click.UsageError:
    """`error` as a HelpfulUsageError of the command it is about; one that
    shows the help already is left as it is."""
    if isinstance(error, (HelpfulUsageError, click.exceptions.NoArgsIsHelpError)):
        return error
    return HelpfulUsageError(error.format_message(), error.ctx or ctx)


class HelpFirstMixin:
    """`--help` anywhere among a command's own arguments is help, whatever
    else is there: click parses every option before it acts on the eager
    one, so `dm49 --help --no-such-option` was an error about the option
    rather than the help asked for. Here the help is shown and the command
    exits before anything is parsed. Only this command's arguments count:
    a `--help` after a subcommand's name is that subcommand's, and it does
    the same for itself. Any usage error, an argument missing, an option
    unknown, a subcommand unknown, or one the command raises itself, is
    shown under the whole help of the command it is about."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        own = args
        if isinstance(self, click.Group):
            # the arguments before the first subcommand name are this
            # group's; anything from the name on is the subcommand's
            names = set(self.list_commands(ctx))
            for index, arg in enumerate(args):
                if arg == "--":
                    own = args[:index]
                    break
                if not arg.startswith("-") and arg in names:
                    own = args[:index]
                    break
        else:
            own = args[: args.index("--")] if "--" in args else args
        if "--help" in own:
            click.echo(ctx.get_help(), color=ctx.color)
            ctx.exit()
        try:
            return super().parse_args(ctx, args)  # type: ignore[misc]
        except click.exceptions.BadOptionUsage as error:
            # an option given without its argument is told what the argument
            # is: the choices when it has them, else the type
            if error.option_name and "requires an argument" in str(error):
                raise HelpfulUsageError(needs_what(self, ctx, error.option_name), error.ctx or ctx) from None
            raise helpful(error, ctx) from None
        except click.UsageError as error:
            raise helpful(error, ctx) from None

    def invoke(self, ctx: click.Context):
        try:
            return super().invoke(ctx)  # type: ignore[misc]
        except click.UsageError as error:
            raise helpful(error, ctx) from None


def needs_what(command: click.Command, ctx: click.Context, option_name: str) -> str:
    """`Option '--view' requires an argument: one of samples, pixels.`, or
    the type's name when the option takes anything of a kind."""
    for param in command.params:
        if option_name in getattr(param, "opts", ()) or option_name in getattr(param, "secondary_opts", ()):
            kind = param.type
            if isinstance(kind, click.Choice):
                return f"Option {option_name!r} requires an argument: one of {', '.join(kind.choices)}."
            metavar = param.metavar or kind.get_metavar(param, ctx) or kind.name.upper()
            return f"Option {option_name!r} requires an argument: {metavar}."
    return f"Option {option_name!r} requires an argument."


class AHMixin(HelpFirstMixin):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        """Options alone are no command either, as when an alias or wrapper
        adds options to every call: a group that shows its help for no
        arguments shows it for those too, instead of failing with "Missing
        command.". click 8.2 keeps the subcommand it parsed, if any, in
        ctx._protected_args."""
        rest = super().parse_args(ctx, args)
        if (
            not ctx._protected_args
            and self.no_args_is_help  # type: ignore[attr-defined]
            and not self.invoke_without_command  # type: ignore[attr-defined]
            and not ctx.resilient_parsing
        ):
            raise click.exceptions.NoArgsIsHelpError(ctx)
        return rest


class AHGroup(AHMixin, click.Group):
    """A group whose --help comes first, whose help shows for options given
    without a subcommand as for no arguments, and whose usage errors, an
    unknown subcommand among them, show its whole help, its subcommands
    listed. Its subcommands are made HelpFirst too."""

    def command(self, *args, **kwargs):
        kwargs.setdefault("cls", AHCommand)
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        kwargs.setdefault("cls", AHGroup)
        return super().group(*args, **kwargs)


class AHCommand(HelpFirstMixin, click.Command):
    pass


class AHCommandCollection(AHMixin, click.CommandCollection):
    pass
