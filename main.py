"""Main script for the bot. This is run, in order to have the bot online."""

# Standard Library Imports
import logging
import json
import traceback
import sys
from datetime import datetime

# 3rd Party Imports
import aiohttp
import discord
from discord.ext import commands

# Custom Imports
import config
from context import Context

class HelpCommand(commands.HelpCommand):
    """Class to handle our help command dynamically."""

    async def send_bot_help(self, _):
        """Will deliver all commands"""
        e = discord.Embed(color=0xFD8063)
        filtered = await self.filter_commands(self.context.bot.commands, sort=True)
        for command in filtered:
            value = command.short_doc
            if value == "":
                value = "No help text specified."

            if command.name == "help":
                pass

            else:
                e.add_field(name=f'!{command.name} {command.signature}', value=value, inline=False)

        await self.get_destination().send(embed=e)

    async def send_command_help(self, command):
        """Will deliver specific commands"""
        e = discord.Embed(title=f'!{command.qualified_name} {command.signature}', color=0xFD8063)
        if command.help == "":
            e.description = "No help text specified."
        else:
            e.description = command.help
        if isinstance(command, commands.Group):
            filtered = await self.filter_commands(command.commands, sort=True)
            for child in filtered:
                if child.short_doc == "":
                    short_doc = "No help text specified."
                else:
                    short_doc = child.short_doc
                e.add_field(name=f'!{child.qualified_name} {child.signature}', value=short_doc, inline=False)

        await self.get_destination().send(embed=e)

    async def send_cog_help(self, cog):
        """Will deliver all commands within a cog"""
        e = discord.Embed(color=0xFD8063)
        filtered = await self.filter_commands(
            cog.get_commands())
        for command in filtered:
            value = command.short_doc
            if value == "":
                value = "No help text specified."

            e.add_field(name=f'!{command.name} {command.signature}', value=value, inline=False)

        await self.get_destination().send(embed=e)

    send_group_help = send_command_help

description = """
Hello. I am a discord bot written by BMan to provide a mutli-purpose utility/moderation service to multiple servers.
"""

log = logging.getLogger(__name__)

initial_extensions = (

)

class MissyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            owner_ids=config.owner_ids,
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            fetch_offline_members=False,
            heartbeat_timeout=150.0,
            allowed_mentions=discord.AllowedMentions(roles=True,everyone=False,users=True),
            intents = discord.Intents.all(),
            case_insensitive=True,
            help_command=HelpCommand()
        )
        self.session = aiohttp.ClientSession(loop=self.loop, trust_env=True)
        self.client_id = config.client_id

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        """
        This fires when the cache has been loaded. This can fire multiple times during the life-cycle of the bot.
        """
        if not hasattr(self, "uptime"):
            setattr(self, "uptime", datetime.utcnow())

        print(f"Ready: {self.user} ID | {self.user.id}", f"\nUsing discord.py v{discord.__version__}")

    async def process_commands(self, message):
        """
        This allows for the bot to automatically process commands on_message
        """
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is None:
            return

        try:
            await self.invoke(ctx)
        except Exception as e:
            print(e)

    async def on_message(self, message):
        """
        This allows the bot to ignore any other bots automagically
        """
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        """
        Clean-up for the bot. Closes the websocket and the client session.
        """
        await super().close()
        await self.session.close()

    def run(self):
        """
        Runs the bot instance
        """
        try:
            super().run(config.token, reconnect=True)

        except Exception as e:
            print(e)

MissyBot().run()
