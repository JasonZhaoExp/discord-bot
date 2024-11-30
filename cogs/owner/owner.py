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


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_bot_owner(self, user_id):
        """Check if the user is the bot owner."""
        return user_id == bot_manager.owner_id

    @commands.group(invoke_without_command=True)
    async def admin(self, ctx):
        """
        Manage bot-level admins.
        Use subcommands like `add`, `remove`, or `list`.
        """
        if not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        await ctx.send("Available subcommands: `add`, `remove`, `list`.")

    @admin.command(name="add")
    async def addadmin(self, ctx, member: discord.Member):
        """Add a user as a bot-level admin."""
        if not self.is_bot_owner(str(ctx.author.id)):
            await ctx.reply("You do not have permission to use this command.", mention_author=True)
            return

        user_id = str(member.id)
        if user_id in bot_manager.admins:
            await ctx.send(f"{member.mention} is already an admin.")
        else:
            bot_manager.admins[user_id] = {"name": member.name}
            await bot_manager.save_users()
            await ctx.send(f"{member.mention} has been added as a bot admin.")

    @admin.command(name="remove")
    async def removeadmin(self, ctx, member: discord.Member):
        """Remove a user from the bot-level admins."""
        if not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        user_id = str(member.id)
        if user_id in bot_manager.admins:
            del bot_manager.admins[user_id]
            await bot_manager.save_users()
            await ctx.send(f"{member.mention} has been removed as a bot admin.")
        else:
            await ctx.send(f"{member.mention} is not an admin.")

    @admin.command(name="list")
    async def list_admins(self, ctx):
        """List all bot-level admins."""
        if not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        if not bot_manager.admins:
            await ctx.send("No admins are currently registered.")
            return

        admin_list = [f"<@{admin_id}> ({admin_info['name']})" for admin_id,
                      admin_info in bot_manager.admins.items()]
        admin_list_str = "\n".join(admin_list)
        embed = discord.Embed(
            title="Registered Admins",
            description=admin_list_str,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def stop(self, ctx):
        """Stop the bot (owner only)."""
        if not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        await ctx.send("Shutting down...")
        await self.bot.close()

    @commands.command()
    async def blacklist(self, ctx, member: discord.Member):
        """Toggle a user's blacklist"""
        if not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        user_id = str(member.id)
        if user_id in bot_manager.blacklist:
            bot_manager.blacklist.remove(user_id)
            await ctx.send(f"{member.mention} has been removed from the blacklist.")
        else:
            bot_manager.blacklist.add(user_id)
            await ctx.send(f"{member.mention} has been added from the blacklist.")

            
# Add cog to bot


async def setup(bot):
    await bot.add_cog(Owner(bot))
