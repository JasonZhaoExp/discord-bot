import discord
from discord.ext import commands
from utils.helpers import bot_manager


class CurrencyAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_bot_owner(self, user_id):
        """Check if the user is the bot owner."""
        return user_id == bot_manager.owner_id

    def is_bot_admin(self, user_id):
        """Check if the user is a bot-level admin."""
        return user_id in bot_manager.admins

    def load_user_data(self, user_id):
        """Retrieve user currency data."""
        user_id = str(user_id)
        if user_id not in bot_manager.currency_data:
            bot_manager.currency_data[user_id] = {"money": 0, "cooldowns": {}}
        return bot_manager.currency_data[user_id]

    @commands.command()
    async def setbalance(self, ctx, member: discord.Member, amount: int):
        """Set the balance of a user (Bot Owner or Admin only)."""
        if not (self.is_bot_owner(str(ctx.author.id)) or self.is_bot_admin(str(ctx.author.id))):
            await ctx.add_reaction("❌")
            return

        user_data = self.load_user_data(member.id)
        user_data["wallet"] = amount

        await bot_manager.save_currency_data()
        await ctx.send(f"Set {member.mention}'s balance to {amount} coins.")

# Add cog to bot


async def setup(bot):
    await bot.add_cog(CurrencyAdmin(bot))
