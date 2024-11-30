# This file is part of VoiceBot.
# VoiceBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# VoiceBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VoiceBot. If not, see <http://www.gnu.org/licenses/>.


import discord
from discord.ext import commands
from utils.helpers import bot_manager
from utils.helpers import is_user_allowed
from config import PREFIX
import datetime
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### AFK SYSTEM ###
    @commands.command()
    @is_user_allowed()
    async def afk(self, ctx, *, message: str = "Not specified"):
        """Set yourself as AFK with an optional message."""
        bot_manager.afk[ctx.author.id] = message
        await ctx.send(f"{ctx.author.mention} is now AFK: {message}")

    ### SNIPE ###
    @commands.command(aliases=["s"])
    @is_user_allowed()
    async def snipe(self, ctx):
        """Retrieve the last deleted message in this channel."""
        guild_id = ctx.guild.id
        if guild_id not in bot_manager.deleted_messages or not bot_manager.deleted_messages[guild_id]:
            await ctx.reply("No recently deleted messages to snipe!")
            return

        sniped_message = bot_manager.deleted_messages[guild_id].pop()
        author = await self.bot.fetch_user(sniped_message["author"])
        await ctx.reply(f"**{author}**: {sniped_message['content']}", mention_author = True)

    ### EDITSNIPE ###
    @commands.command(aliases=["es"])
    @is_user_allowed()
    async def editsnipe(self, ctx):
        """Retrieve the last edited message in this channel."""
        guild_id = ctx.guild.id
        if guild_id not in bot_manager.edited_messages or not bot_manager.edited_messages[guild_id]:
            await ctx.send("No recently edited messages to snipe!")
            return

        edited_message = bot_manager.edited_messages[guild_id].pop()
        author = await self.bot.fetch_user(edited_message["author"])
        await ctx.send(
            f"**{author}** edited their message:\n"
            f"**Before:** {edited_message['old_content']}\n"
            f"**After:** {edited_message['new_content']}"
        )

    @commands.group(invoke_without_command=True)
    @is_user_allowed()
    async def summon(self, ctx):
        f"""
        Base summon command. Pings everyone in the summon list.
        Use `{PREFIX}summon list` to view the summon list without pinging.
        """
        user_id = str(ctx.author.id)
        if user_id in bot_manager.summons and bot_manager.summons[user_id]:
            mentions = [
                f"<@{member_id}>" for member_id in bot_manager.summons[user_id]
            ]
            await ctx.send(f"{ctx.author.mention} is summoning: {', '.join(mentions)}")
        else:
            await ctx.send("Your summon list is empty!")

    @summon.command(name="add")
    @is_user_allowed()
    async def summon_add(self, ctx, member: discord.Member):
        """Add a member to your summon list."""
        user_id = str(ctx.author.id)
        bot_manager.summons.setdefault(user_id, [])
        if member.id not in bot_manager.summons[user_id]:
            bot_manager.summons[user_id].append(member.id)
            await bot_manager.save_summons()
            await ctx.send(f"{member.mention} has been added to your summon list.")
        else:
            await ctx.send(f"{member.mention} is already in your summon list.")

    @summon.command(name="remove")
    @is_user_allowed()
    async def summon_remove(self, ctx, member: discord.Member):
        """Remove a member from your summon list."""
        user_id = str(ctx.author.id)
        if user_id in bot_manager.summons and member.id in bot_manager.summons[user_id]:
            bot_manager.summons[user_id].remove(member.id)
            await bot_manager.save_summons()
            await ctx.send(f"{member.mention} has been removed from your summon list.")
        else:
            await ctx.send(f"{member.mention} is not in your summon list.")

    @summon.command(name="clear")
    @is_user_allowed()
    async def summon_clear(self, ctx):
        """Clear your entire summon list."""
        user_id = str(ctx.author.id)
        if user_id in bot_manager.summons:
            bot_manager.summons[user_id] = []
            await bot_manager.save_summons()
            await ctx.send("Your summon list has been cleared.")
        else:
            await ctx.send("You don't have a summon list to clear!")

    @summon.command(name="list")
    @is_user_allowed()
    async def summon_list(self, ctx):
        """List all users in your summon list without pinging."""
        user_id = str(ctx.author.id)
        if user_id in bot_manager.summons and bot_manager.summons[user_id]:
            member_names = [
                self.bot.get_user(member_id).name
                for member_id in bot_manager.summons[user_id]
                if self.bot.get_user(member_id)
            ]
            member_list = ", ".join(member_names)
            await ctx.send(f"Your summon list: {member_list}")
        else:
            await ctx.send("Your summon list is empty!")
    
    @commands.group(name="birthday", invoke_without_command=True)
    async def birthday_group(self, ctx):
        """Main group for birthday-related commands."""
        await ctx.send("Available subcommands: set, remove, check, today")

    @birthday_group.command(name="set")
    async def set_birthday(self, ctx, date: str):
        """
        Set your birthday in DD-MM format.
        :param date: The birthday date (e.g., "25-12").
        """
        try:
            user_id = str(ctx.author.id)
            # Validate date format
            datetime.strptime(date, "%d-%m")
            bot_manager.birthdays[user_id] = date
            await bot_manager.save_birthdays()
            await ctx.send(f"Your birthday has been set to {date}.")
        except ValueError:
            await ctx.send("Invalid date format. Please use DD-MM.")

    @birthday_group.command(name="remove")
    async def remove_birthday(self, ctx):
        """Remove your birthday from the tracker."""
        user_id = str(ctx.author.id)
        if user_id in bot_manager.birthdays:
            del bot_manager.birthdays[user_id]
            await bot_manager.save_birthdays()
            await ctx.send("Your birthday has been removed.")
        else:
            await ctx.send("You do not have a birthday set.")

    @birthday_group.command(name="check")
    async def check_birthday(self, ctx, member: commands.MemberConverter = None):
        """
        Check someone's birthday.
        :param member: The member to check (defaults to the caller).
        """
        member = member or ctx.author
        user_id = str(member.id)
        birthday = bot_manager.birthdays.get(user_id)
        if birthday:
            await ctx.send(f"{member.display_name}'s birthday is on {birthday}.")
        else:
            await ctx.send(f"{member.display_name} has not set a birthday.")

    @birthday_group.command(name="today")
    async def birthdays_today(self, ctx):
        """List all users who have their birthday today."""
        today = time.strftime("%d-%m")
        birthday_users = [
            ctx.guild.get_member(int(user_id))
            for user_id, date in bot_manager.birthdays.items()
            if date == today
        ]
        if birthday_users:
            mentions = ", ".join([member.mention for member in birthday_users if member])
            await ctx.send(f"🎉 Today's birthdays: {mentions}")
        else:
            await ctx.send("No birthdays today.")


# Add cog to bot
async def setup(bot):
    await bot.add_cog(Utility(bot))
