import os
import random
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

import database


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

DAILY_COOLDOWN_HOURS = 24
RAID_COOLDOWN_HOURS = 1
RAID_MIN_TARGET_BALANCE = 50
RAID_SUCCESS_CHANCE = 0.4

ONE_PIECE_API_BASE = "https://api.api-onepiece.com/v2"

ROASTS = [
    "Your bounty is 3 berries and one of them is counterfeit.",
    "Even Buggy has more useful leadership skills than you.",
    "You're not a pirate, you're a deckhand with Wi-Fi.",
    "Your Observation Haki must be broken—you didn't see that coming.",
    "You've got the confidence of a Yonko and the fighting ability of a Sea King.",
    "Your crew didn't abandon you. They just finally found better Wi-Fi.",
    "Even Usopp would need a better story to explain how bad that was.",
    "Your navigation skills make Zoro look like a GPS.",
    "You're the kind of pirate who gets defeated by the tutorial island.",
    "Your Devil Fruit would be the Yap-Yap no Mi.",
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def extract_text(value, fallback="Unknown"):
    if value is None or value == "":
        return fallback
    if isinstance(value, dict):
        return value.get("name", fallback)
    return str(value)


@bot.command()
async def duel(ctx, choice: str = None):
    valid_choices = ["rock", "paper", "scissors"]

    if choice is None or choice.lower() not in valid_choices:
        await ctx.send("Usage: `!duel rock` / `!duel paper` / `!duel scissors`")
        return

    database.get_user(ctx.author.id, str(ctx.author))

    player_choice = choice.lower()
    bot_choice = random.choice(valid_choices)
    wager = 50

    if player_choice == bot_choice:
        result_text = f"⚔️ Both drew **{player_choice}**. It's a draw, no Berries change hands."
    elif (
        (player_choice == "rock" and bot_choice == "scissors")
        or (player_choice == "paper" and bot_choice == "rock")
        or (player_choice == "scissors" and bot_choice == "paper")
    ):
        database.add_to_balance(ctx.author.id, wager)
        result_text = (
            f"⚔️ You chose **{player_choice}**, the bot chose **{bot_choice}**.\n"
            f"You win the swordfight and take **{wager} Berries**!"
        )
    else:
        database.add_to_balance(ctx.author.id, -wager)
        result_text = (
            f"⚔️ You chose **{player_choice}**, the bot chose **{bot_choice}**.\n"
            f"You lose the swordfight and drop **{wager} Berries**."
        )

    await ctx.send(result_text)


def now_str():
    return datetime.utcnow().isoformat()


@bot.command()
async def raid(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Usage: `!raid @user`")
        return

    if member.id == ctx.author.id:
        await ctx.send("You can't raid your own ship.")
        return

    attacker_row = database.get_user(ctx.author.id, str(ctx.author))
    last_rob = attacker_row[4]

    hours_passed = hours_since(last_rob)
    if hours_passed is not None and hours_passed < RAID_COOLDOWN_HOURS:
        hours_left = RAID_COOLDOWN_HOURS - hours_passed
        await ctx.send(f"🏴‍☠️ Your crew needs to rest. Try raiding again in {format_cooldown(hours_left)}.")
        return

    target_row = database.get_user(member.id, str(member))
    target_balance = target_row[2]

    if target_balance < RAID_MIN_TARGET_BALANCE:
        await ctx.send(f"{member.display_name}'s stash is too small to bother raiding.")
        return

    database.set_last_rob(ctx.author.id, now_str())

    success = random.random() < RAID_SUCCESS_CHANCE

    if success:
        stolen = random.randint(10, 30)
        stolen_amount = int(target_balance * (stolen / 100))
        stolen_amount = max(stolen_amount, 1)

        database.add_to_balance(member.id, -stolen_amount)
        database.add_to_balance(ctx.author.id, stolen_amount)

        await ctx.send(
            f"💥 Raid successful! {ctx.author.display_name} stole **{stolen_amount} Berries** "
            f"from {member.display_name}'s stash."
        )
    else:
        penalty = random.randint(20, 60)
        database.add_to_balance(ctx.author.id, -penalty)
        await ctx.send(
            f"🚨 The raid failed! {ctx.author.display_name} got caught and paid "
            f"**{penalty} Berries** in damages."
        )


@bot.command()
async def worstgeneration(ctx):
    top_users = database.get_top_users(5)

    if not top_users:
        await ctx.send("No pirates have made a name for themselves yet.")
        return

    medals = ["🥇", "🥈", "🥉", "4.", "5."]
    lines = ["🏆 **Worst Generation Leaderboard** 🏆"]
    for i, (username, balance) in enumerate(top_users):
        lines.append(f"{medals[i]} {username} - {balance} Berries")

    await ctx.send("\n".join(lines))


def hours_since(timestamp_str):
    if timestamp_str is None:
        return None
    last_time = datetime.fromisoformat(timestamp_str)
    diff = datetime.utcnow() - last_time
    return diff.total_seconds() / 3600


@bot.command()
async def roast(ctx, member: discord.Member = None):
    target = member or ctx.author
    insult = random.choice(ROASTS)
    await ctx.send(f"🔥 {target.display_name}, {insult}")


@bot.command()
async def bounty(ctx, member: discord.Member = None):
    target = member or ctx.author
    row = database.get_user(target.id, str(target))
    balance = row[2]
    await ctx.send(f"💰 {target.display_name}'s current bounty: **{balance} Berries**")


@bot.command()
async def logpose(ctx):
    await ctx.send("🧭 The Log Pose is spinning...")

    async with aiohttp.ClientSession() as session:
        try:
            pick = random.choice(["character", "fruit"])

            if pick == "character":
                async with session.get(f"{ONE_PIECE_API_BASE}/characters/en") as resp:
                    data = await resp.json()
                character = random.choice(data)
                name = extract_text(character.get("name"), "Unknown Pirate")
                bounty_amt = extract_text(character.get("bounty"), "Unknown")
                crew = extract_text(character.get("crew"), "No crew on record")
                await ctx.send(
                    f"📜 **Wanted:** {name}\n"
                    f"**Crew:** {crew}\n"
                    f"**Bounty:** {bounty_amt}"
                )
            else:
                async with session.get(f"{ONE_PIECE_API_BASE}/fruits/en") as resp:
                    data = await resp.json()
                fruit = random.choice(data)
                name = extract_text(fruit.get("name"), "Unknown Fruit")
                ftype = extract_text(fruit.get("type"), "Unknown type")
                description = extract_text(fruit.get("description"), "No description available.")
                await ctx.send(
                    f"🍎 **Devil Fruit:** {name}\n"
                    f"**Type:** {ftype}\n"
                    f"**Power:** {description}"
                )
        except Exception:
            await ctx.send(
                "The Log Pose spun wildly and lost the signal. Try again in a bit, the intel network's down."
            )


def format_cooldown(hours_left):
    total_minutes = int(hours_left * 60)
    hrs = total_minutes // 60
    mins = total_minutes % 60
    if hrs > 0:
        return f"{hrs}h {mins}m"
    return f"{mins}m"


@bot.command()
async def trade(ctx, member: discord.Member = None, amount: int = None):
    if member is None or amount is None:
        await ctx.send("Usage: `!trade @user <amount>`")
        return

    if member.id == ctx.author.id:
        await ctx.send("You can't trade with yourself, rookie.")
        return

    if amount <= 0:
        await ctx.send("Nice try. Trade amount has to be a positive number.")
        return

    sender_row = database.get_user(ctx.author.id, str(ctx.author))
    sender_balance = sender_row[2]

    if amount > sender_balance:
        await ctx.send("You don't have that many Berries to trade.")
        return

    database.get_user(member.id, str(member))

    database.add_to_balance(ctx.author.id, -amount)
    database.add_to_balance(member.id, amount)

    await ctx.send(f"🤝 {ctx.author.display_name} traded **{amount} Berries** to {member.display_name}.")


@bot.command()
async def setsail(ctx):
    row = database.get_user(ctx.author.id, str(ctx.author))
    last_daily = row[3]

    hours_passed = hours_since(last_daily)
    if hours_passed is not None and hours_passed < DAILY_COOLDOWN_HOURS:
        hours_left = DAILY_COOLDOWN_HOURS - hours_passed
        await ctx.send(
            f"⚓ Your crew already set sail today. Come back in {format_cooldown(hours_left)}."
        )
        return

    reward = random.randint(100, 400)
    database.add_to_balance(ctx.author.id, reward)
    database.set_last_daily(ctx.author.id, now_str())

    await ctx.send(
        f"🏴‍☠️ You raided a merchant ship at dawn and made off with **{reward} Berries**!"
    )


@bot.event
async def on_ready():
    print(f"The Berry Broker is open for business. Logged in as {bot.user}")


def main():
    if TOKEN is None:
        print("No DISCORD_TOKEN found. Add it to your .env file first.")
        return
    database.init_db()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
