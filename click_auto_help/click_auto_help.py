#!/usr/bin/env python3

import click


class AHMixin:
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
    pass


class AHCommandCollection(AHMixin, click.CommandCollection):
    pass
