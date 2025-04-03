import discord
from discord.ext import commands
import json
import re
import os
from database import save_join_code, get_join_code, delete_join_code, clear_all_codes  # Import DB functions

TOKEN = os.getenv("TOKEN")
# Load configuration from JSON file
with open("config.json", "r") as file:
    config = json.load(file)


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    """Detect join codes and store/update them"""
    if message.author == bot.user:
        return

    match = re.findall(r"join code[:\-]?\s*([\w\s]+#\d+(\s*\+\s*[\w\s]+#\d+)*)", message.content, re.IGNORECASE)
    if match:
        join_codes = match[0][0].split(" + ")  # Handle multiple codes

        for join_code in join_codes:
            save_join_code(message.author.id, join_code)

        await message.channel.send(
            f"✅ {message.author.mention}, your join code(s) `{', '.join(join_codes)}` have been saved!"
        )

    await bot.process_commands(message)

@bot.command()
async def joincode(ctx, member: discord.Member = None):
    """Retrieve a user's join code"""
    member = member or ctx.author  # Default to command sender

    result = get_join_code(member.id)

    if result:
        await ctx.send(f"🎮 {member.mention}'s join code: `{result}`")
    else:
        await ctx.send(f"❌ {member.mention} has not saved a join code yet!")

@bot.command()
async def deletecode(ctx):
    """Allow users to delete their own join code"""
    delete_join_code(ctx.author.id)
    await ctx.send(f"🗑️ {ctx.author.mention}, your join code has been deleted!")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearallcodes(ctx):
    """Allow admins to delete all join codes"""
    clear_all_codes()
    await ctx.send("⚠️ **All join codes have been deleted by an admin!**")

@clearallcodes.error
async def clearallcodes_error(ctx, error):
    """Error handler for admin command"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"⛔ {ctx.author.mention}, you don't have permission to use this command!")

bot.run(TOKEN)
