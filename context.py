"""
Subclassing the Context model for easier reaction usage and access to web sessions if using an API is necessary.
"""

# Standard Library Imports
import asyncio

# 3rd Party Imports
from discord.ext import commands

# Custom Imports
from config import *

yes = '\N{WHITE HEAVY CHECK MARK}'
no = "\N{CROSS MARK}"
maybe = "\N{WARNING SIGN}"


class Context(commands.Context):
    """Custom class, subclassing context so we can override methods
    
    Adding a session property to context
    
    Also adding interactive prompt."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    async def prompt(self,msg, *, timeout=60.0, delete_after=True,author_id=None, responses: dict=None):
        """An interactive reaction confirmation dialog.

        Args:
            msg: str
                The message to show along with the prompt.
            timeout: float
                How long to wait before returning
            delete_after: bool
                Whether to delete the confirmation message once we're done.
            author_id: Optional[int]
                The member who is expected to respond to the prompt.
                    Defaults to the author of the Context's message.

        Returns:
            Optional[bool]:
                ``True`` if explicit confirmation
                ``False`` if explicit denial
                ``None`` if timeout occured
        """

        if not self.channel.permissions_for(self.me).add_reactions:
            raise RuntimeError("Bot does not had `Add Reaction` permissions.")

        fmt = f"{msg}\n\nReact with {yes} to **confirm** or {no} to **decline**."

        author_id = author_id or self.author.id
        msg = await self.send(fmt)

        confirm = None

        def check(payload):
            nonlocal confirm

            if payload.message_id != msg.id or payload.user_id != author_id:
                return False

            codepoint = str(payload.emoji)

            if codepoint == yes:
                confirm = True
                return True

            elif codepoint == no:
                confirm = False
                return True

            return False

        for emoji in (yes, no):
            await msg.add_reaction(emoji)

        try:
            await self.bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None

        try:
            if delete_after:
                await msg.delete()

        except Exception as e:
            print(e)

        finally:
            await msg.clear_reactions()
            try:
                response = responses[confirm]
                await msg.edit(content=response)
            except KeyError:
                if confirm is True:
                    await msg.edit(content="Positive feedback received.")
                elif confirm is False:
                    await msg.edit(content="Negative feedback received.")
                elif confirm is None:
                    await msg.edit(content="Timeout occured. Please try again.")
            except Exception as e:
                print(e)
            return confirm

    async def tick(self, msg, reaction):
        """Helper method to add a reation to a message.

        Args:
            reaction: bool
                ``True``: Reacts with a checkmark
                ``False``: Reacts with an X
                ``None``: Reacts with a generic slash
        """
        lookup = {
            True: yes,
            False: no,
            None: maybe
        }
        emoji = lookup.get(reaction)
        await msg.add_reaction(emoji)
        return emoji
