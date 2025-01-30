#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tab-width:4


"""
Extension for ``click`` to provide a group
which automatically prints a list of valid
commands when a invaild command is used.
Based off click-didyoumean.
https://github.com/click-contrib/click-didyoumean
"""
from __future__ import annotations

import typing

import click


class AHMixin:
    """
    Mixin class for click MultiCommand inherited classes
    to provide a list of valid commands when
    a certain command is not registered.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore

    def resolve_command(
        self,
        ctx: click.Context,
        args: list[str],
    ) -> tuple[
        None | str,
        None | click.Command,
        list[str],
    ]:
        """
        Overrides clicks ``resolve_command`` method
        and appends list of valid commands to the
        raised exception message.
        """
        try:
            # pylint: disable=no-member
            return super(AHMixin, self).resolve_command(ctx, args)  # type: ignore
            # pylint: enable=no-member
        except click.exceptions.UsageError as error:
            error_msg = str(error)
            # pylint: disable=no-member
            matches = self.list_commands(ctx)  # type: ignore
            # pylint: enable=no-member
            if matches:
                fmt_matches = "\n    ".join(matches)
                error_msg += "\n\n"
                error_msg += f"Defined commands:\n    {fmt_matches}"

            raise click.exceptions.UsageError(error_msg, error.ctx)


class AHGroup(AHMixin, click.Group):
    """
    click Group to provide a list of
    valid commands when a command is not
    found in the group.
    """


class AHCommandCollection(AHMixin, click.CommandCollection):
    """
    click CommandCollection to provide a list
    of valid commands when a command is not
    found in the group.
    """
