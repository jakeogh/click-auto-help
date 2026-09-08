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
        return super().parse_args(ctx, args)  # type: ignore[misc]


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
