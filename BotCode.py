import discord
from discord.ext import commands
import sqlite3
import json
import re

import os
TOKEN = os.getenv("TOKEN")

# Load configuration from JSON file
with open("config.json", "r") as file:
    config = json.load(file)

CHANNEL_ID = config.get("CHANNEL_ID")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
conn = sqlite3.connect("join_codes.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS join_codes (
        user_id INTEGER PRIMARY KEY,  -- Ensures user_id is unique
        code TEXT
    )
""")
conn.commit()


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")


@bot.event
async def on_message(message):
    """Detect join codes and store/update them"""
    if message.author == bot.user:
        return

    match = re.search(r"join code[:\-]?\s*(\S+#\d+)", message.content, re.IGNORECASE)
    if match:
        join_code = match.group(1)

        # Insert or update the join code
        cursor.execute("""
            INSERT INTO join_codes (user_id, code) 
            VALUES (?, ?) 
            ON CONFLICT(user_id) DO UPDATE SET code=excluded.code;
        """, (message.author.id, join_code))

        conn.commit()

        await message.channel.send(
            f"✅ {message.author.mention}, your join code `{join_code}` has been saved!"
        )

    await bot.process_commands(message)


@bot.command()
async def joincode(ctx, member: discord.Member = None):
    """Retrieve a user's join code"""
    member = member or ctx.author  # Default to command sender if no user is mentioned

    cursor.execute("SELECT code FROM join_codes WHERE user_id=?", (member.id,))
    result = cursor.fetchone()

    if result:
        await ctx.send(f"🎮 {member.mention}'s join code: `{result[0]}`")
    else:
        await ctx.send(f"❌ {member.mention} has not saved a join code yet!")


@bot.command()
async def deletecode(ctx):
    """Allow users to delete their own join code"""
    cursor.execute("DELETE FROM join_codes WHERE user_id=?", (ctx.author.id,))
    conn.commit()
    await ctx.send(f"🗑️ {ctx.author.mention}, your join code has been deleted!")


@bot.command()
@commands.has_permissions(administrator=True)
async def clearallcodes(ctx):
    """Allow admins to delete all join codes"""
    cursor.execute("DELETE FROM join_codes")
    conn.commit()
    await ctx.send("⚠️ **All join codes have been deleted by an admin!**")


@clearallcodes.error
async def clearallcodes_error(ctx, error):
    """Error handler for admin command"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"⛔ {ctx.author.mention}, you don't have permission to use this command!")


bot.run(TOKEN)
