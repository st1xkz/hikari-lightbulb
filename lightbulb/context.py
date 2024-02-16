# -*- coding: utf-8 -*-
# Copyright (c) 2023-present tandemdude
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

__all__ = ["Context"]

import dataclasses
import typing as t

if t.TYPE_CHECKING:
    import hikari

    from lightbulb import client as client_
    from lightbulb import commands


@dataclasses.dataclass(slots=True)
class Context:
    client: client_.Client

    interaction: hikari.CommandInteraction
    options: t.Sequence[hikari.CommandInteractionOption]

    command: commands.CommandBase

    def __post_init__(self) -> None:
        self.command._set_context(self)

    @property
    def guild_id(self) -> t.Optional[hikari.Snowflake]:
        return self.interaction.guild_id

    @property
    def channel_id(self) -> hikari.Snowflake:
        return self.interaction.channel_id

    @property
    def user(self) -> hikari.User:
        return self.interaction.user

    @property
    def member(self) -> t.Optional[hikari.InteractionMember]:
        return self.interaction.member

    @property
    def command_data(self) -> commands.CommandData:
        return self.command._command_data
