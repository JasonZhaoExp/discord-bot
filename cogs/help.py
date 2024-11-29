# VoiceBot - Multifeature discord bot, made for Voicebox's Kingdom
# Copyright (C) 2024  Jason Zhao
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import discord
from discord.ext import commands
from utils.helpers import bot_manager
from config import PREFIX


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "Other Commands"
        self.command_attrs["name"] = "help"

    async def send_bot_help(self, mapping):
        """Send help for all commands the user can access."""
        ctx = self.context
        bot = ctx.bot
        user_id = str(ctx.author.id)

        embed = discord.Embed(
            title="Help", description="Available Commands", color=discord.Color.blurple())
        embed.set_footer(text=f"Use {PREFIX}help <command> for more info.")

        # Check if the bot is paused
        if bot_manager.paused:
            embed.description = "The bot is currently paused and commands are disabled."
            return await ctx.send(embed=embed)

        # Check user roles
        is_owner = user_id == bot_manager.owner_id
        is_admin = user_id in bot_manager.admins
        is_user = user_id in bot_manager.users

        # Iterate over cogs and commands
        for cog, commands in mapping.items():
            filtered_commands = []
            for command in commands:
                # Filter commands based on access level
                if await self._can_user_run_command(ctx, command, is_owner, is_admin, is_user):
                    filtered_commands.append(command)

            # Add commands to embed if any are accessible
            if filtered_commands:
                cog_name = cog.qualified_name if cog else self.no_category
                command_list = "\n".join(
                    f"`{command.name}`" for command in filtered_commands)
                embed.add_field(
                    name=cog_name, value=command_list, inline=False)

        # If no commands are available
        if not embed.fields:
            embed.description = "You do not have access to any commands."

        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        """Send detailed help for a specific command."""
        embed = discord.Embed(
            title=f"Help: {command.qualified_name}",
            description=command.help or "No description provided.",
            color=discord.Color.blurple(),
        )

        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(
                command.aliases), inline=False)
        embed.add_field(
            name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)

        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        """Send help for a command group."""
        embed = discord.Embed(
            title=f"Help: {group.qualified_name}",
            description=group.help or "No description provided.",
            color=discord.Color.blurple(),
        )

        if group.aliases:
            embed.add_field(name="Aliases", value=", ".join(
                group.aliases), inline=False)

        filtered_commands = await self.filter_commands(group.commands)
        if filtered_commands:
            embed.add_field(
                name="Subcommands",
                value="\n".join(
                    f"`{command.name}` - {command.help or 'No description'}" for command in filtered_commands),
                inline=False,
            )

        await self.context.send(embed=embed)

    async def _can_user_run_command(self, ctx, command, is_owner, is_admin, is_user):
        """
        Determine if the user can see a command based on their role.
        """
        return True
        # print(f"Checking command: {command.name} | Cog: {command.cog.qualified_name if command.cog else 'None'}")
        # print(f"is_owner: {is_owner}, is_admin: {is_admin}, is_user: {is_user}, global_restricted: {bot_manager.global_restricted}")

        # if is_owner:
        #     print(f"Allowing {ctx.author} as owner.")
        #     return True

        # if "admin" in command.cog.qualified_name.lower():
        #     print(f"Checking admin command: {command.name}")
        #     return is_admin

        # if "owner" in command.cog.qualified_name.lower():
        #     print(f"Owner command restricted to owner only: {command.name}")
        #     return False

        # if not bot_manager.global_restricted or is_user:
        #     try:
        #         print(f"Checking permissions for user-level command: {command.name}")
        #         return await command.can_run(ctx)
        #     except commands.CommandError as e:
        #         print(f"Command {command.name} failed permission check: {e}")
        #         return False

        # print(f"Command {command.name} not accessible for user.")
        # return False


    async def filter_commands(self, commands, *, sort=False):
        """Filter commands to only those the user can use."""
        ctx = self.context
        user_id = str(ctx.author.id)

        is_owner = user_id == bot_manager.owner_id
        is_admin = user_id in bot_manager.admins
        is_user = user_id in bot_manager.users

        filtered = []
        for command in commands:
            if await self._can_user_run_command(ctx, command, is_owner, is_admin, is_user):
                filtered.append(command)

        if sort:
            filtered.sort(key=lambda c: c.name)
        return filtered


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = CustomHelpCommand()

    def cog_unload(self):
        self.bot.help_command = commands.DefaultHelpCommand()


# Add cog to bot
async def setup(bot):
    await bot.add_cog(HelpCog(bot))
