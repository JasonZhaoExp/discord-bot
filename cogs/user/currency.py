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
from discord.ext import commands, tasks
from Crypto.Random import random
import time
import asyncio
from utils.helpers import bot_manager, is_user_allowed
from config import PREFIX


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apply_interest_task.start()

    def get_user_data(self, user_id):
        """Retrieve or initialize data for a user."""
        user_id = str(user_id)
        if user_id not in bot_manager.currency_data:
            bot_manager.currency_data[user_id] = {
                "wallet": 0,
                "bank": 0,
                "daily_claimed": False,
            }
        return bot_manager.currency_data[user_id]

    async def handle_cooldown(self, ctx, user_id, cooldown_key, reward, cooldown_time):
        """
        Handle cooldown-based currency commands (daily, weekly, monthly).
        :param ctx: Command context.
        :param user_id: User's ID.
        :param cooldown_key: The cooldown key to track.
        :param reward: The reward amount.
        :param cooldown_time: Cooldown duration in seconds.
        """
        user_data = self.get_user_data(user_id)
        now = time.time()
        last_used = user_data.get(cooldown_key, 0)

        if now - last_used < cooldown_time:
            remaining = cooldown_time - (now - last_used)

            # Calculate remaining time
            # 86400 seconds in a day
            days, remainder = divmod(int(remaining), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format the message
            if days > 0:
                time_message = f"{days}d {hours}h {minutes}m {seconds}s"
            else:
                time_message = f"{hours}h {minutes}m {seconds}s"

            await ctx.send(
                f"You need to wait {time_message} before claiming again, {ctx.author.mention}!"
            )
            return

        # Update user data
        user_data["wallet"] += reward
        user_data[cooldown_key] = now
        await bot_manager.save_currency_data()

        await ctx.send(f"{ctx.author.mention}, you claimed {reward} coins!")

    @commands.command(aliases=["bal"])
    @is_user_allowed()
    async def wallet(self, ctx):
        """
        Display the user's wallet balance.
        """
        user_id = str(ctx.author.id)
        user_data = self.get_user_data(user_id)

        wallet_balance = user_data.get("wallet", 0)

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Wallet Balance 💰",
            description=f"**Wallet:** {wallet_balance} coins",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Keep earning more coins to increase your balance!")

        await ctx.send(embed=embed)

    @commands.command()
    @is_user_allowed()
    async def daily(self, ctx):
        """Claim your daily reward."""
        await self.handle_cooldown(ctx, ctx.author.id, "last_daily", 500, 86400)

    @commands.command()
    @is_user_allowed()
    async def weekly(self, ctx):
        """Claim your weekly reward."""
        await self.handle_cooldown(ctx, ctx.author.id, "last_weekly", 3500, 604800)

    @commands.command()
    @is_user_allowed()
    async def monthly(self, ctx):
        """Claim your monthly reward."""
        await self.handle_cooldown(ctx, ctx.author.id, "last_monthly", 15000, 2592000)

    @commands.command()
    @is_user_allowed()
    async def gamble(self, ctx, amount: int):
        """Gamble a specific amount of money."""
        if amount <= 0:
            await ctx.send("You can only gamble a positive amount of money.")
            return

        user_id = str(ctx.author.id)
        user_data = self.get_user_data(user_id)

        if user_data["wallet"] < amount:
            await ctx.send("You don't have enough money in your wallet to gamble that amount.")
            return
        
        if bool(random.getrandbits(1)):
            user_data["wallet"] += amount
            await ctx.send(f"Congratulations {ctx.author.mention}, you won {amount} coins!")
        else:
            user_data["wallet"] -= amount
            await ctx.send(f"Sorry {ctx.author.mention}, you lost {amount} coins.")

        await bot_manager.save_currency_data()

    @commands.command()
    @is_user_allowed()
    async def beg(self, ctx):
        """Beg for coins with an hour-long cooldown."""
        user_id = str(ctx.author.id)
        user_data = self.get_user_data(user_id)

        now = time.time()
        last_beg = user_data.get("last_beg", 0)
        cooldown = 300

        if now - last_beg < cooldown:
            remaining = cooldown - (now - last_beg)
            minutes, seconds = divmod(int(remaining), 60)
            await ctx.send(
                f"You need to wait {minutes}m {seconds}s before you can beg again, {ctx.author.mention}!"
            )
            return
        
        if bool(random.getrandbits(1)):
            reward = random.randint(10, 250)
            if user_id == "691738362612154449":
                reward = random.randint(10, 150)
            user_data["wallet"] += reward
            user_data["last_beg"] = now

            await bot_manager.save_currency_data()
            await ctx.send(f"{ctx.author.mention}, you begged and received {reward} coins!")
        else:
            user_data["last_beg"] = now
            await ctx.send(f"{ctx.author.mention}, you begged and recieved nothing")

    @commands.command()
    @is_user_allowed()
    async def bankruptcy(self, ctx):
        """Reset balance to 500 and set all cooldowns to maximum."""
        user_id = str(ctx.author.id)
        user_data = self.get_user_data(user_id)

        now = time.time()
        last_bankruptcy = user_data.get("last_bankruptcy", 0)
        cooldown = 3600

        if now - last_bankruptcy < cooldown:
            remaining = cooldown - (now - last_bankruptcy)
            minutes, seconds = divmod(int(remaining), 60)
            await ctx.send(
                f"You need to wait {minutes}m {seconds}s before you can beg again, {ctx.author.mention}!"
            )
            return

        # Update user data
        user_data.update({
            "wallet": 500,
            "bank": 0,
            "last_daily": now,
            "last_weekly": now,
            "last_monthly": now,
            "last_bankruptcy": now,
        })

        await bot_manager.save_currency_data()
        await ctx.send(
            f"{ctx.author.mention}, you've declared bankruptcy! Your balance is now 500 coins, "
            "and all cooldowns have been set to their maximum."
        )

    @commands.command(aliases=["lb"])
    @is_user_allowed()
    async def leaderboard(self, ctx, page: int = 1):
        """
        Display a paginated leaderboard.
        :param page: The page number to display.
        """
        # Constants
        items_per_page = 10  # Number of users to display per page
        total_users = len(bot_manager.currency_data)

        # Calculate pagination
        total_pages = (total_users + items_per_page - 1) // items_per_page
        if page < 1 or page > total_pages:
            await ctx.send(f"Invalid page number. Please select a page between 1 and {total_pages}.")
            return

        # Retrieve and sort user data by total currency (wallet + bank)
        sorted_data = sorted(
            bot_manager.currency_data.items(),
            key=lambda item: item[1].get("wallet", 0) + item[1].get("bank", 0),
            reverse=True
        )

        # Determine start and end indices for the page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = sorted_data[start_idx:end_idx]

        # Create the leaderboard message
        leaderboard_message = f"**🏆 Leaderboard (Page {page}/{total_pages}) 🏆**\n\n"
        for i, (user_id, data) in enumerate(page_data, start=start_idx + 1):
            user = self.bot.get_user(int(user_id))
            username = user.name if user else f"User {user_id}"
            wallet = data.get("wallet", 0)
            bank = data.get("bank", 0)
            total = wallet + bank
            leaderboard_message += f"{i}. {username}: {total} coins (Wallet: {wallet}, Bank: {bank})\n"

        # Add navigation footer
        leaderboard_message += f"\nUse `,lb <page>` to view other pages."

        # Send the leaderboard message
        await ctx.send(leaderboard_message)

    @commands.group(invoke_without_command=True)
    @is_user_allowed()
    async def wager(self, ctx):
        f"""Base command for wagers. Use `{PREFIX}wager coinflip` or `{PREFIX}wager dice`."""
        await ctx.send(f"Please specify a game type: `{PREFIX}wager coinflip` or `{PREFIX}wager dice`.")

    @wager.command(aliases=["cf"])
    @is_user_allowed()
    async def coinflip(self, ctx, opponent: discord.Member, amount: int):
        """
        Challenge another user to a coin flip wager.
        :param opponent: The user being challenged.
        :param amount: The wager amount.
        """
        if amount <= 0:
            await ctx.send("The wager amount must be greater than zero.")
            return

        challenger_id = str(ctx.author.id)
        opponent_id = str(opponent.id)

        challenger_data = self.get_user_data(challenger_id)
        opponent_data = self.get_user_data(opponent_id)

        if challenger_data["wallet"] < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough coins for this wager.")
            return

        if opponent_data["wallet"] < amount:
            await ctx.send(f"{opponent.mention} doesn't have enough coins for this wager.")
            return

        await ctx.send(f"{ctx.author.mention}, do you choose heads or tails? Type `heads` or `tails`.")

        def check_heads_or_tails(m):
            return m.author == ctx.author and m.content.lower() in ["heads", "tails"]

        try:
            challenger_choice_msg = await self.bot.wait_for("message", timeout=30.0, check=check_heads_or_tails)
            challenger_choice = challenger_choice_msg.content.lower()
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, you took too long to respond. Wager canceled.")
            return

        opponent_choice = "tails" if challenger_choice == "heads" else "heads"

        wager_msg = (
            f"{opponent.mention}, {ctx.author.mention} has challenged you to a coin flip wager!\n"
            f"You: {opponent_choice}\n"
            f"{ctx.author.mention}: {challenger_choice}\n"
            f"Amount: {amount}\n"
            f"Do you accept? Type `yes` or `no`."
        )
        await ctx.send(wager_msg)

        def check_opponent_response(m):
            return m.author == opponent and m.content.lower() in ["yes", "no"]

        try:
            opponent_response_msg = await self.bot.wait_for("message", timeout=30.0, check=check_opponent_response)
            opponent_response = opponent_response_msg.content.lower()
        except asyncio.TimeoutError:
            await ctx.send(f"{opponent.mention}, you took too long to respond. Wager canceled.")
            return

        if opponent_response == "no":
            await ctx.send(f"{opponent.mention} declined the wager. Wager canceled.")
            return

        result = "heads" if bool(random.getrandbits(1)) else "tails"
        winner = ctx.author if result == challenger_choice else opponent
        loser = opponent if result == challenger_choice else ctx.author

        winner_data = self.get_user_data(winner.id)
        loser_data = self.get_user_data(loser.id)

        winner_data["wallet"] += amount
        loser_data["wallet"] -= amount

        await bot_manager.save_currency_data()

        await ctx.send(
            f"The coin landed on **{result}**!\n"
            f"Congratulations, {winner.mention}! You won {amount} coins from {loser.mention}."
        )

    @wager.command()
    @is_user_allowed()
    async def dice(self, ctx, opponent: discord.Member, amount: int):
        """
        Challenge another user to a dice roll wager.
        :param opponent: The user being challenged.
        :param amount: The wager amount.
        """
        if amount <= 0:
            await ctx.send("The wager amount must be greater than zero.")
            return

        challenger_id = str(ctx.author.id)
        opponent_id = str(opponent.id)

        challenger_data = self.get_user_data(challenger_id)
        opponent_data = self.get_user_data(opponent_id)

        # Check if both users have enough currency
        if challenger_data["wallet"] < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough coins for this wager.")
            return

        if opponent_data["wallet"] < amount:
            await ctx.send(f"{opponent.mention} doesn't have enough coins for this wager.")
            return

        # Announce the wager challenge
        wager_msg = (
            f"{opponent.mention}, {ctx.author.mention} has challenged you to a dice roll wager!\n"
            f"Amount: {amount}\n"
            f"Do you accept? Type `yes` or `no`."
        )
        await ctx.send(wager_msg)

        def check_opponent_response(m):
            return m.author == opponent and m.content.lower() in ["yes", "no"]

        try:
            opponent_response_msg = await self.bot.wait_for("message", timeout=30.0, check=check_opponent_response)
            opponent_response = opponent_response_msg.content.lower()
        except asyncio.TimeoutError:
            await ctx.send(f"{opponent.mention}, you took too long to respond. Wager canceled.")
            return

        if opponent_response == "no":
            await ctx.send(f"{opponent.mention} declined the wager. Wager canceled.")
            return

        # Roll the dice
        challenger_roll = random.randint(1, 6)
        opponent_roll = random.randint(1, 6)

        # Determine winner
        if challenger_roll > opponent_roll:
            winner = ctx.author
            loser = opponent
        elif opponent_roll > challenger_roll:
            winner = opponent
            loser = ctx.author
        else:
            await ctx.send(
                f"It's a tie! Both rolled **{challenger_roll}**. No coins are exchanged."
            )
            return

        # Adjust balances
        winner_data = self.get_user_data(winner.id)
        loser_data = self.get_user_data(loser.id)

        winner_data["wallet"] += amount
        loser_data["wallet"] -= amount

        await bot_manager.save_currency_data()

        # Announce the results
        await ctx.send(
            f"{ctx.author.mention} rolled **{challenger_roll}**, and {opponent.mention} rolled **{opponent_roll}**!\n"
            f"🎲 {winner.mention} wins {amount} coins from {loser.mention}!"
        )

    @commands.group(invoke_without_command=True)
    @is_user_allowed()
    async def shop(self, ctx):
        """Manage the shop. Use subcommands like 'show', 'buy', or 'sell'."""
        await ctx.send("Use `,shop show`, `,shop buy <item>`, or `,shop sell <item>`.")

    # @shop.command()
    # @is_user_allowed()
    # async def show(self, ctx):
    #     """Show available items in the shop."""
    #     shop = bot_manager.data_cache["shop"]
    #     if not shop:
    #         await ctx.send("The shop is currently empty!")
    #         return

    #     shop_message = "**🛒 Shop Items:**\n\n"
    #     for item, price in shop.items():
    #         shop_message += f"{item}: {price} coins\n"

    #     await ctx.send(shop_message)

    # @shop.command()
    # @is_user_allowed()
    # async def buy(self, ctx, *, item_name):
    #     """Buy an item from the shop."""
    #     item_name = item_name.lower()
    #     user_id = str(ctx.author.id)
    #     currency_data = bot_manager.currency_data
    #     inventory = bot_manager.get_inventory(user_id)

    #     shop = bot_manager.data_cache["shop"]
    #     if item_name not in shop:
    #         await ctx.send(f"{ctx.author.mention}, that item is not available in the shop.")
    #         return

    #     price = shop[item_name]
    #     if currency_data[user_id]["wallet"] < price:
    #         await ctx.send(f"{ctx.author.mention}, you don't have enough coins to buy {item_name}.")
    #         return

    #     # Deduct money and add item to inventory
    #     currency_data[user_id]["wallet"] -= price
    #     inventory.append(item_name)
    #     await bot_manager.save_inventory()
    #     await bot_manager.save_currency_data()

    #     await ctx.send(f"{ctx.author.mention}, you bought {item_name} for {price} coins!")

    # @shop.command()
    # @is_user_allowed()
    # async def sell(self, ctx, *, item_name):
    #     """Sell an item from your inventory."""
    #     item_name = item_name.lower()
    #     user_id = str(ctx.author.id)
    #     currency_data = bot_manager.currency_data
    #     inventory = bot_manager.get_inventory(user_id)

    #     shop = bot_manager.data_cache["shop"]
    #     if item_name not in inventory:
    #         await ctx.send(f"{ctx.author.mention}, you don't have {item_name} in your inventory.")
    #         return

    #     if item_name not in shop:
    #         await ctx.send(f"{ctx.author.mention}, you cannot sell {item_name} to the shop.")
    #         return

    #     # Calculate the sell price (30% of the shop price)
    #     sell_price = int(shop[item_name] * 0.3)

    #     # Remove item from inventory and add money
    #     inventory.remove(item_name)
    #     currency_data[user_id]["wallet"] += sell_price

    #     await bot_manager.save_inventory()
    #     await bot_manager.save_currency_data()

    #     await ctx.send(f"{ctx.author.mention}, you sold {item_name} for {sell_price} coins!")

    # @commands.command()
    # @is_user_allowed()
    # async def fish(self, ctx):
    #     """Go fishing. Requires a fishing rod and has a cooldown."""
    #     user_id = str(ctx.author.id)
    #     inventory = bot_manager.get_inventory(user_id)
    #     cooldown_time = 3600  # 1 hour cooldown

    #     # Check if the user has a fishing rod
    #     if "fishing rod" not in inventory:
    #         await ctx.send(f"{ctx.author.mention}, you need a fishing rod to go fishing! Buy one from the shop!")
    #         return

    #     # Get the user's data
    #     currency_data = bot_manager.currency_data
    #     if user_id not in currency_data:
    #         currency_data[user_id] = {"wallet": 0, "last_fish": 0}

    #     # Check cooldown
    #     now = time.time()
    #     last_fish = currency_data[user_id].get("last_fish", 0)
    #     if now - last_fish < cooldown_time:
    #         remaining = cooldown_time - (now - last_fish)
    #         hours, remainder = divmod(int(remaining), 3600)
    #         minutes, seconds = divmod(remainder, 60)
    #         time_message = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
    #         await ctx.send(f"{ctx.author.mention}, you need to wait {time_message} before fishing again!")
    #         return

    #     # Get the fishing loot table
    #     loot_table = bot_manager.get_loot_table("fishing")
    #     if not loot_table:
    #         await ctx.send(f"{ctx.author.mention}, the fishing loot table is empty. Contact an admin.")
    #         return

    #     # Prepare weighted choices
    #     total_weight = sum(fish["weight"] for fish in loot_table)
    #     rand = random.randint(0, total_weight)
    #     upto = 0
    #     selected_fish = None
    #     for fish in loot_table:
    #         if upto + fish["weight"] >= rand:
    #             selected_fish = fish
    #             break
    #         upto += fish["weight"]

    #     if not selected_fish:
    #         await ctx.send(f"{ctx.author.mention}, something went wrong with the fishing loot table. Contact an admin.")
    #         return

    #     # Determine fish weight and payout
    #     weight = round(random.randint(
    #         selected_fish["min_weight"], selected_fish["max_weight"]), 2)
    #     payout = int(weight * selected_fish["payout_per_kg"])

    #     # Update the user's currency and cooldown
    #     currency_data[user_id]["wallet"] += payout
    #     currency_data[user_id]["last_fish"] = now

    #     # Save the updated data
    #     await bot_manager.save_currency_data()

    #     # Notify the user
    #     await ctx.send(
    #         f"{ctx.author.mention}, you caught a {weight}kg {selected_fish['rarity']} {selected_fish['name']} and earned {payout} coins!"
    #     )

    @commands.group()
    @is_user_allowed()
    async def bank(self, ctx):
        """Banking operations: deposit, withdraw, balance."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"{ctx.author.mention}, please specify a subcommand: deposit, withdraw, or balance.")

    @bank.command()
    @is_user_allowed()
    async def deposit(self, ctx, amount: int):
        """Deposit money into your bank account."""
        user_id = str(ctx.author.id)
        user_data = bot_manager.currency_data.get(
            user_id, {"wallet": 0, "bank": 0, "last_interest_time": 0})

        if amount <= 0:
            await ctx.send(f"{ctx.author.mention}, please enter a positive amount to deposit.")
            return

        if user_data["wallet"] < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough money in your wallet.")
            return

        user_data["wallet"] -= amount
        user_data["bank"] += amount
        bot_manager.currency_data[user_id] = user_data
        await bot_manager.save_currency_data()
        await ctx.send(f"{ctx.author.mention}, you have deposited {amount} coins into your bank account.")

    @bank.command()
    @is_user_allowed()
    async def withdraw(self, ctx, amount: int):
        """Withdraw money from your bank account."""
        user_id = str(ctx.author.id)
        user_data = bot_manager.currency_data.get(
            user_id, {"wallet": 0, "bank": 0, "last_interest_time": 0})

        if amount <= 0:
            await ctx.send(f"{ctx.author.mention}, please enter a positive amount to withdraw.")
            return

        if user_data["bank"] < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough money in your bank account.")
            return

        user_data["bank"] -= amount
        user_data["wallet"] += amount
        bot_manager.currency_data[user_id] = user_data
        await bot_manager.save_currency_data()
        await ctx.send(f"{ctx.author.mention}, you have withdrawn {amount} coins from your bank account.")

    @bank.command(aliases=["bal"])
    @is_user_allowed()
    async def balance(self, ctx):
        """
        Display the user's wallet balance.
        """
        user_id = str(ctx.author.id)
        user_data = self.get_user_data(user_id)

        bank_balance = user_data.get("bank", 0)

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Bank Balance 💰",
            description=f"**Bank:** {bank_balance} coins",
            color=discord.Color.gold()
        )
        embed.set_footer(
            text=f"Keep depositing coins to your bank! There's a 1% interest rate each day!")

        await ctx.send(embed=embed)

    async def apply_interest(self):
        """Apply interest to all users' bank balances."""
        current_time = time.time()
        for user_id, data in bot_manager.currency_data.items():
            last_interest_time = data.get("last_interest_time", 0)
            if current_time - last_interest_time >= 86400:
                interest = data["bank"] * 0.01
                data["bank"] += interest
                data["last_interest_time"] = current_time
        await bot_manager.save_currency_data()

    # @commands.command()
    # @is_user_allowed()
    # async def trade(self, ctx, other_user: discord.Member):
    #     """Initiate a trade between two users."""
    #     if other_user == ctx.author:
    #         await ctx.send(f"{ctx.author.mention}, you cannot trade with yourself.")
    #         return

    #     def check_response(m):
    #         return m.author == other_user and m.channel == ctx.channel

    #     await ctx.send(f"{other_user.mention}, {ctx.author.mention} wants to trade with you. Type `yes` to accept or `no` to decline.")

    #     try:
    #         response = await self.bot.wait_for("message", timeout=30.0, check=check_response)
    #     except asyncio.TimeoutError:
    #         await ctx.send(f"{ctx.author.mention}, {other_user.mention} did not respond. Trade canceled.")
    #         return

    #     if response.content.lower() != "yes":
    #         await ctx.send(f"{ctx.author.mention}, {other_user.mention} declined the trade. Trade canceled.")
    #         return

    #     await ctx.send(f"{ctx.author.mention} and {other_user.mention}, you can now make offers. Use `offer <item/coins>` to propose, or type `accept` or `decline` to finalize the trade.")

    #     # Initialize trade data
    #     trade_data = {
    #         "user1": {"id": ctx.author.id, "offer": None},
    #         "user2": {"id": other_user.id, "offer": None}
    #     }

    #     def check_offer(m):
    #         return m.author.id in [ctx.author.id, other_user.id] and m.channel == ctx.channel

    #     async def display_trade_status():
    #         """Display the current state of the trade."""
    #         user1_offer = trade_data["user1"]["offer"] or "Nothing"
    #         user2_offer = trade_data["user2"]["offer"] or "Nothing"
    #         await ctx.send(
    #             f"**Trade Status**:\n"
    #             f"{ctx.author.mention} offered: {user1_offer}\n"
    #             f"{other_user.mention} offered: {user2_offer}\n\n"
    #             f"Use `offer <item/coins>` to update your offer, or `accept`/`decline` to finalize."
    #         )

    #     while True:
    #         try:
    #             user_message = await self.bot.wait_for("message", timeout=120.0, check=check_offer)
    #         except asyncio.TimeoutError:
    #             await ctx.send("Trade timed out due to inactivity. Trade canceled.")
    #             return

    #         user = ctx.author if user_message.author.id == ctx.author.id else other_user
    #         user_key = "user1" if user.id == ctx.author.id else "user2"

    #         if user_message.content.lower() == "decline":
    #             await ctx.send(f"{ctx.author.mention} and {other_user.mention}, the trade has been canceled.")
    #             return

    #         if user_message.content.lower() == "accept":
    #             if trade_data["user1"]["offer"] and trade_data["user2"]["offer"]:
    #                 # Process the trade
    #                 user1_data = self.get_user_data(ctx.author.id)
    #                 user2_data = self.get_user_data(other_user.id)

    #                 # Perform the trade
    #                 user1_offer = trade_data["user1"]["offer"]
    #                 user2_offer = trade_data["user2"]["offer"]

    #                 # Check offers validity and update inventories or wallets
    #                 if isinstance(user1_offer, int):
    #                     if user1_data["wallet"] < user1_offer:
    #                         await ctx.send(f"{ctx.author.mention}, you don't have enough coins to complete this trade.")
    #                         return
    #                     user1_data["wallet"] -= user1_offer
    #                     user2_data["wallet"] += user1_offer
    #                 else:
    #                     if user1_offer not in user1_data["inventory"]:
    #                         await ctx.send(f"{ctx.author.mention}, you no longer have the item `{user1_offer}`.")
    #                         return
    #                     user1_data["inventory"].remove(user1_offer)
    #                     user2_data["inventory"].append(user1_offer)

    #                 if isinstance(user2_offer, int):
    #                     if user2_data["wallet"] < user2_offer:
    #                         await ctx.send(f"{other_user.mention}, you don't have enough coins to complete this trade.")
    #                         return
    #                     user2_data["wallet"] -= user2_offer
    #                     user1_data["wallet"] += user2_offer
    #                 else:
    #                     if user2_offer not in user2_data["inventory"]:
    #                         await ctx.send(f"{other_user.mention}, you no longer have the item `{user2_offer}`.")
    #                         return
    #                     user2_data["inventory"].remove(user2_offer)
    #                     user1_data["inventory"].append(user2_offer)

    #                 await bot_manager.save_currency_data()
    #                 await ctx.send(
    #                     f"Trade completed successfully!\n"
    #                     f"{ctx.author.mention} gave: {user1_offer}\n"
    #                     f"{other_user.mention} gave: {user2_offer}"
    #                 )
    #                 return
    #             else:
    #                 await ctx.send("Both parties must make an offer before accepting the trade.")
    #                 continue

    #         if user_message.content.startswith("offer "):
    #             offer = user_message.content[6:].strip()
    #             try:
    #                 if offer.isdigit():
    #                     offer = int(offer)
    #                 else:
    #                     offer = offer.lower()  # Normalize item names
    #             except ValueError:
    #                 await ctx.send("Invalid offer. Use `offer <item/coins>`.")
    #                 continue

    #             trade_data[user_key]["offer"] = offer
    #             await display_trade_status()

    @tasks.loop(seconds=86400)
    async def apply_interest_task(self):
        await self.apply_interest()

    @apply_interest_task.before_loop
    async def before_apply_interest(self):
        await self.bot.wait_until_ready()


# Add cog to bot
async def setup(bot):
    await bot.add_cog(Currency(bot))
