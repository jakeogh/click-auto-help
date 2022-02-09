#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tab-width:4


"""
Extension for ``click`` to provide a group
which automatically prints --help when a
invaild command is used.
Based off click-didyoumean.
"""

#import difflib
import typing

import click


class DYMMixin:
    """
    Mixin class for click MultiCommand inherited classes
    to provide full --help functionality when
    a certain command is not registered.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.max_suggestions = kwargs.pop("max_suggestions", 3)
        self.cutoff = kwargs.pop("cutoff", 0.5)
        super().__init__(*args, **kwargs)  # type: ignore

    def resolve_command(
        self, ctx: click.Context, args: typing.List[str]
    ) -> typing.Tuple[
        typing.Optional[str], typing.Optional[click.Command], typing.List[str]
    ]:
        """
        Overrides clicks ``resolve_command`` method
        and appends *Did you mean ...* suggestions
        to the raised exception message.
        """
        try:
            return super(DYMMixin, self).resolve_command(ctx, args)  # type: ignore
        except click.exceptions.UsageError as error:
            error_msg = str(error)
            original_cmd_name = click.utils.make_str(args[0])
            matches = self.list_commands(ctx) # type: ignore
            if matches:
                fmt_matches = "\n    ".join(matches)
                error_msg += "\n\n"
                error_msg += f"Did ya mean one of these?\n    {fmt_matches}"

            raise click.exceptions.UsageError(error_msg, error.ctx)


class DYMGroup(DYMMixin, click.Group):
    """
    click Group to provide full --help
    functionality when a command is not
    found in the group.
    """


class DYMCommandCollection(DYMMixin, click.CommandCollection):
    """
    click CommandCollection to provide full
    --help functionality when a command is
    not found in the group.
    """
