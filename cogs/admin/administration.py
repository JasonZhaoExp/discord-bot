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


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_bot_admin(self, user_id):
        """Check if the user is a bot-level admin."""
        return user_id in bot_manager.admins

    def is_bot_owner(self, user_id):
        """Check if the user is the bot owner."""
        return user_id == bot_manager.owner_id

    @commands.group(invoke_without_command=True)
    async def user(self, ctx):
        """
        Manage bot-level users.
        Use subcommands like `add`, `remove`, or `list`.
        """
        await ctx.send("Available subcommands: `add`, `remove`, `list`.")

    @user.command(name="add")
    async def adduser(self, ctx, member: discord.Member):
        """Add a user to the bot-level users."""
        if not self.is_bot_admin(str(ctx.author.id)) and not self.is_bot_owner(str(ctx.author.id)):
            await ctx.send("You do not have permission to use this command.")
            return

        user_id = str(member.id)
        if user_id in bot_manager.users:
            await ctx.send(f"{member.mention} is already a registered user.")
        else:
            bot_manager.users[user_id] = {"name": member.name}
            await bot_manager.save_users()
            await ctx.send(f"{member.mention} has been added as a bot user.")

    @user.command(name="remove")
    async def removeuser(self, ctx, member: discord.Member):
        """Remove a user from the bot-level users."""
        if not self.is_bot_admin(str(ctx.author.id)) and not self.is_bot_owner(str(ctx.author.id)):
            await ctx.send("You do not have permission to use this command.")
            return

        user_id = str(member.id)
        if user_id in bot_manager.users:
            del bot_manager.users[user_id]
            await bot_manager.save_users()
            await ctx.send(f"{member.mention} has been removed as a bot user.")
        else:
            await ctx.send(f"{member.mention} is not a registered user.")

    @user.command(name="list")
    async def list_users(self, ctx):
        """List all registered bot-level users."""
        if not self.is_bot_admin(str(ctx.author.id)) and not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        if not bot_manager.users:
            await ctx.send("No users are currently registered.")
            return

        user_list = [f"<@{user_id}> ({user_info['name']})" for user_id,
                     user_info in bot_manager.users.items()]
        user_list_str = "\n".join(user_list)
        embed = discord.Embed(
            title="Registered Users",
            description=user_list_str,
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def toggle_access(self, ctx):
        """Toggle global user access restriction."""
        if not self.is_bot_admin(str(ctx.author.id)) and not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        bot_manager.global_restricted = not bot_manager.global_restricted
        state = "restricted to users" if bot_manager.global_restricted else "open to everyone"
        await ctx.send(f"Global access is now {state}.")


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
