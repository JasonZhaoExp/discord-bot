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

from discord.ext import commands
from utils.helpers import bot_manager


class AdminUtilities(commands.Cog):
    @commands.command(aliases=["cs"])
    async def clearsnipes(self, ctx):
        """Clear the snipe and editsnipe caches."""
        guild_id = ctx.guild.id
        if guild_id in bot_manager.deleted_messages:
            bot_manager.deleted_messages[guild_id].clear()
        if guild_id in bot_manager.edited_messages:
            bot_manager.edited_messages[guild_id].clear()
        await ctx.send("Cleared the snipe and editsnipe caches.")

    @commands.command()
    async def pause(self, ctx):
        """Pause the bot."""
        if not self.is_bot_admin(str(ctx.author.id)) and not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        bot_manager.paused = True
        await ctx.send("Bot functionality has been paused.")

    @commands.command()
    async def unpause(self, ctx):
        """Unpause the bot."""
        if not self.is_bot_admin(str(ctx.author.id)) and not self.is_bot_owner(str(ctx.author.id)):
            await ctx.add_reaction("❌")
            return

        bot_manager.paused = False
        await ctx.send("Bot functionality has been resumed.")


async def setup(bot):
    await bot.add_cog(AdminUtilities(bot))
