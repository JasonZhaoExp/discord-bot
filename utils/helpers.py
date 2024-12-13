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


from discord.ext.commands import CheckFailure
import json
import time
from collections import defaultdict, deque
from discord.ext import commands
from PIL import Image


class BotManager:
    """A class to manage bot-related data and operations."""

    def __init__(self):
        self.owner_id = None
        self.admins = {}
        self.users = {}
        self.afk = {}
        self.summons = {}
        self.currency_data = {}
        self.blacklist = set()
        self.deleted_messages = defaultdict(deque)
        self.edited_messages = defaultdict(deque)
        self.global_restricted = False
        self.paused = False
        self.data_files = {
            "users": "data/user_ids.json",
            "summons": "data/summons.json",
            "currency": "data/currency.json",
            "inventory": "data/inventory.json",
            "shop": "data/shop.json",
            "loot_tables": "data/loottables.json",
        }
        self.data_cache = {
            "users": {},
            "summons": {},
            "currency": {},
            "inventory": {},
            "shop": {},
            "loot_tables": {},
        }

    async def load_data(self, key):
        """
        Load data from a file based on a key.
        :param key: The identifier for the data (e.g., "currency").
        """
        file_path = self.data_files.get(key)
        if not file_path:
            print(f"Error: No file path mapped for key '{key}'.")
            return {}
        try:
            with open(file_path, "r") as file:
                self.data_cache[key] = json.load(file)
                return self.data_cache[key]
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error loading data from {file_path}. Using defaults.")
            self.data_cache[key] = {}
            return {}

    async def save_data(self, key):
        """
        Save data to a file based on a key.
        :param key: The identifier for the data (e.g., "currency").
        """
        file_path = self.data_files.get(key)
        if not file_path:
            print(f"Error: No file path mapped for key '{key}'.")
            return
        try:
            with open(file_path, "w") as file:
                json.dump(self.data_cache[key], file, indent=4)
        except Exception as e:
            print(f"Error saving data to {file_path}: {e}")

    # Specialized methods to manage user data
    async def load_users(self):
        """Load user-related data."""
        self.data_cache["users"] = await self.load_data("users")
        self.owner_id = self.data_cache["users"].get("owner")
        self.admins = {int(k): v for k, v in self.data_cache["users"].get(
            "admins", {}).items()}
        self.users = {int(k): v for k, v in self.data_cache["users"].get(
            "users", {}).items()}

    async def save_users(self):
        """Save user-related data."""
        self.data_cache["users"] = {
            "owner": self.owner_id,
            "admins": {str(k): v for k, v in self.admins.items()},
            "users": {str(k): v for k, v in self.users.items()},
        }
        await self.save_data("users")

    # Specialized methods for summons
    async def load_summons(self):
        """Load summon-related data."""
        self.data_cache["summons"] = await self.load_data("summons")

    async def save_summons(self):
        """Save summon-related data."""
        await self.save_data("summons")

    async def load_currency_data(self):
        """Load currency data from the JSON file."""
        try:
            with open("data/currency.json", "r") as file:
                self.currency_data = json.load(file)
                # Initialize missing fields
                for user_id, data in self.currency_data.items():
                    if "wallet" not in data:
                        data["wallet"] = 0
                    if "bank" not in data:
                        data["bank"] = 0
                    if "last_interest_time" not in data:
                        data["last_interest_time"] = time.time()
        except (FileNotFoundError, json.JSONDecodeError):
            print("Currency data not found or invalid. Initializing with empty data.")
            self.currency_data = {}

    async def save_currency_data(self):
        """Save currency data to the JSON file."""
        try:
            with open("data/currency.json", "w") as file:
                json.dump(self.currency_data, file, indent=4)
        except Exception as e:
            print(f"Error saving currency data: {e}")

    # Inventory management
    def get_inventory(self, user_id):
        """Retrieve or initialize a user's inventory."""
        user_id = str(user_id)
        if user_id not in self.data_cache["inventory"]:
            self.data_cache["inventory"][user_id] = []
        return self.data_cache["inventory"][user_id]

    async def save_inventory(self):
        """Save inventory data."""
        await self.save_data("inventory")

    # Shop management
    async def load_shop(self):
        """Load shop data."""
        self.data_cache["shop"] = await self.load_data("shop")

    async def save_shop(self):
        """Save shop data."""
        await self.save_data("shop")

        # Loot table management
    async def load_loot_tables(self):
        """Load loot table data."""
        self.data_cache["loot_tables"] = await self.load_data("loot_tables")

    def get_loot_table(self, table_name):
        """Retrieve a specific loot table by name."""
        return self.data_cache["loot_tables"].get(table_name, [])

    # Helper to clean up old messages
    def clean_old_entries(self, cache, age_limit=900, max_entries=50):
        """
        Remove old entries from the cache.
        :param cache: The deque to clean.
        :param age_limit: Maximum age in seconds for an entry (default 15 minutes).
        :param max_entries: Maximum number of entries in the cache.
        """
        current_time = time.time()
        while cache and (
            current_time -
                cache[0]["timestamp"] > age_limit or len(cache) > max_entries
        ):
            cache.popleft()
    
    # Birthday-related methods
    async def load_birthdays(self):
        """Load birthday data from the JSON file."""
        try:
            with open(self.data_files["birthdays"], "r") as file:
                self.birthdays = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Birthdays data not found or invalid. Initializing with empty data.")
            self.birthdays = {}

    async def save_birthdays(self):
        """Save birthday data to the JSON file."""
        try:
            with open(self.data_files["birthdays"], "w") as file:
                json.dump(self.birthdays, file, indent=4)
        except Exception as e:
            print(f"Error saving birthdays data: {e}")

    def set_birthday(self, user_id, date):
        """
        Set a user's birthday.
        :param user_id: The ID of the user.
        :param date: The birthday date in "DD-MM" format.
        """
        self.birthdays[str(user_id)] = date

    def remove_birthday(self, user_id):
        """
        Remove a user's birthday.
        :param user_id: The ID of the user.
        """
        if str(user_id) in self.birthdays:
            del self.birthdays[str(user_id)]
        
    def get_birthday(self, user_id):
        """
        Retrieve a user's birthday.
        :param user_id: The ID of the user.
        :return: The birthday date in "DD-MM" format, or None if not set.
        """
        return self.birthdays.get(str(user_id))

    def get_today_birthdays(self):
        """
        Retrieve a list of user IDs whose birthdays are today.
        :return: List of user IDs.
        """
        today = time.strftime("%d-%m")
        return [user_id for user_id, birthday in self.birthdays.items() if birthday == today]

    def add_deleted_message(self, guild_id, message):
        """Add a deleted message to the cache."""
        self.deleted_messages[guild_id].append(
            {"content": message.content, "author": message.author.id,
                "timestamp": time.time()}
        )
        self.clean_old_entries(self.deleted_messages[guild_id])

    def add_edited_message(self, guild_id, old_message, new_message):
        """Add an edited message to the cache."""
        self.edited_messages[guild_id].append(
            {
                "old_content": old_message.content,
                "new_content": new_message.content,
                "author": old_message.author.id,
                "timestamp": time.time(),
            }
        )
        self.clean_old_entries(self.edited_messages[guild_id])


class NotAuthorized(CheckFailure):
    """Custom exception for unauthorized access."""


bot_manager = BotManager()


def is_user_allowed():
    """Check if the user is permitted to use the bot."""
    def predicate(ctx):
        # Check if the bot is paused
        if bot_manager.paused:
            raise NotAuthorized("The bot is currently paused.")

        user_id = str(ctx.author.id)

        # If user blacklisted, disallow
        if user_id in bot_manager.blacklist:
            return False

        # If global restriction is off, allow all users
        if not bot_manager.global_restricted:
            return True

        # Check if the user is a registered user or higher
        if user_id in bot_manager.users or user_id in bot_manager.admins or user_id == bot_manager.owner_id:
            return True

        # Otherwise, deny access
        raise NotAuthorized("You do not have permission to use this command.")
    return commands.check(predicate)

def resize_image(input_path, output_path, size):
    with Image.open(input_path) as img:
        img = img.resize(size, Image.ANTIALIAS)
        img.save(output_path)
