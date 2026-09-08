#!/usr/bin/env python3

import click


class HelpFirstMixin:
    """`--help` anywhere among a command's own arguments is help, whatever
    else is there: click parses every option before it acts on the eager
    one, so `dm49 --help --no-such-option` was an error about the option
    rather than the help asked for. Here the help is shown and the command
    exits before anything is parsed. Only this command's arguments count:
    a `--help` after a subcommand's name is that subcommand's, and it does
    the same for itself."""

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
                raise click.exceptions.BadOptionUsage(
                    error.option_name, needs_what(self, ctx, error.option_name), error.ctx
                ) from None
            raise


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
    # appends the list of valid commands to the UsageError raised for an
    # unknown command; based on click-didyoumean
    def resolve_command(
        self,
        ctx: click.Context,
        args: list[str],
    ) -> tuple[None | str, None | click.Command, list[str]]:
        try:
            return super().resolve_command(ctx, args)  # type: ignore[misc]
        except click.exceptions.UsageError as error:
            error_msg = str(error)
            matches = self.list_commands(ctx)  # type: ignore[attr-defined]
            if matches:
                fmt_matches = "\n    ".join(matches)
                error_msg += f"\n\nDefined commands:\n    {fmt_matches}"
            raise click.exceptions.UsageError(error_msg, error.ctx)


class AHGroup(AHMixin, click.Group):
    """A group whose --help comes first, and whose unknown subcommand names
    the ones there are. Its subcommands are made HelpFirst too."""

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
