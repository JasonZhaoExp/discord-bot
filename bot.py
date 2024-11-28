"""
    VoiceBot - Multifeature discord bot, made for Voicebox's Kingdom
    Copyright (C) 2024  Jason Zhao

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import os
import asyncio
import discord
import time

from discord.ext import commands
from collections import deque
from config import TOKEN, PREFIX
from utils.helpers import bot_manager, is_user_allowed

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


async def load_extensions():
    """Load all cogs dynamically."""
    for folder in ["user", "admin", "owner"]:
        folder_path = f"cogs/{folder}"
        for file in os.listdir(folder_path):
            if file.endswith(".py") and not file.startswith("__"):
                extension = f"cogs.{folder}.{file[:-3]}"
                try:
                    await bot.load_extension(extension)
                    print(f"Loaded extension: {extension}")
                except Exception as e:
                    print(f"Failed to load extension {extension}: {e}")

    """Load help command"""
    try:
        await bot.load_extension("cogs.help")
        print(f"Loaded extension: cogs.help")
    except Exception as e:
        print(f"Failed to load help: {e}")


@bot.event
async def on_ready():
    print("ready")
    await bot_manager.load_users()
    await bot_manager.load_summons()
    await bot_manager.load_currency_data()
    await bot_manager.load_shop()
    await bot_manager.load_loot_tables()
    print(f"Logged in as {bot.user}")
    print("Available Commands:")
    for command in bot.commands:
        print(f"{command.name}: {command.help or 'No description'}")


@bot.event
async def on_message(message):
    print(message)
    if message.author.bot or not is_user_allowed():
        print(message.author)
        return

    # Check if user is AFK and clear status
    if message.author.id in bot_manager.afk:
        del bot_manager.afk[message.author.id]
        await message.channel.send(f"Welcome back, {message.author.mention}! You are no longer AFK.")

    # Notify if someone mentions an AFK user
    for user in message.mentions:
        print(user)
        if user.id in bot_manager.afk:
            afk_message = bot_manager.afk[user.id]
            user = await bot.fetch_user(user.id)
            await message.channel.send(f"{user} is AFK: {afk_message}")

    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    """Cache deleted messages for snipe."""
    if message.author.bot or not message.guild:
        return

    guild_id = message.guild.id
    bot_manager.deleted_messages.setdefault(guild_id, deque(maxlen=50)).append({
        "content": message.content,
        "author": message.author.id,
        "timestamp": time.time()
    })


@bot.event
async def on_message_edit(before, after):
    """Cache edited messages for editsnipe."""
    if before.author.bot or not before.guild:
        return

    guild_id = before.guild.id
    bot_manager.edited_messages.setdefault(guild_id, deque(maxlen=50)).append({
        "old_content": before.content,
        "new_content": after.content,
        "author": before.author.id,
        "timestamp": time.time()
    })


async def main():
    """Main entry point for the bot."""
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
