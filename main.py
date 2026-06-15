import discord
from discord.ext import commands
import random
import os
import asyncio
from flask import Flask
from threading import Thread

# ==================== WEB SERVER FOR KEEP ALIVE ====================
app = Flask('')

@app.route('/')
def home():
    return "Tw Money Slots Game for All Servers is Online!"

def run_web():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================== SETUP DISCORD BOT ====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

# Raw Emoji Code
OWNER_PHOTO_EMOJI = "<:emoji_2:1515950500208578622>"

# EMOJI VALUE MULTIPLIERS
EMOJI_VALUES = {
    OWNER_PHOTO_EMOJI: 10,  # JACKPOT GRAND PRIZE (x10)
    '7️⃣': 7,
    '💎': 5,
    '🍊': 4,
    '🍇': 3,
    '🍓': 2,
    '🍒': 1.5
}

SLOTS_EMOJIS = list(EMOJI_VALUES.keys())
user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} for ALL SERVERS is Ready!")

# ==================== 🎰 SLOTS COMMAND (Tw [bet]) ====================
@bot.command(name="Tw")
async def play_slots(ctx, bet: str = None):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id not in user_balances:
        user_balances[user_id] = 0
        
    if bet is None:
        return await ctx.send(f"❌ Please enter a bet amount! Example: Tw 50 or Tw all (Balance: {user_balances[user_id]} {custom_coin})")
    
    if bet.lower() == "all":
        bet_amount = user_balances[user_id]
    else:
        try:
            bet_amount = int(bet)
        except ValueError:
            return await ctx.send("❌ Bet amount must be a number or all!")
            
    if bet_amount <= 0:
        return await ctx.send("❌ Bet amount must be greater than 0!")
        
    if bet_amount > user_balances[user_id]:
        return await ctx.send(f"❌ You don't have enough money! Balance: {user_balances[user_id]} {custom_coin} (Type Twork to earn money)")

    slot1 = random.choice(SLOTS_EMOJIS)
    slot2 = random.choice(SLOTS_EMOJIS)
    slot3 = random.choice(SLOTS_EMOJIS)
    
    # ==================== WIN / LOSE CALCULATION ====================
    if slot1 == slot2 == slot3:
        multiplier = EMOJI_VALUES[slot1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        
        status_text = "🎉 JACKPOT! YOU WIN! 🎉"
        reward_text = f"💵 Received: +{win_amount} {custom_coin}\n💰 Total: {user_balances[user_id]} {custom_coin}"
        msg_color = 0x00ff00
        
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        matched_emoji = slot2 if slot2 == slot3 or slot1 == slot2 else slot1
        multiplier = EMOJI_VALUES[matched_emoji] / 2
        win_amount = int(bet_amount * multiplier)
        if win_amount < 1: win_amount = 1
        
        user_balances[user_id] += win_amount
        status_text = "💵 2 MATCH VALUE! 💵"
        reward_text = f"💵 Received: +{win_amount} {custom_coin}\n💰 Total: {user_balances[user_id]} {custom_coin}"
        msg_color = 0x3498db
        
    else:
        user_balances[user_id] -= bet_amount
        status_text = "❌ YOU LOSE! ❌"
        reward_text = f"📉 Lost: -{bet_amount} {custom_coin}\n💰 Balance: {user_balances[user_id]} {custom_coin}"
        msg_color = 0xe74c3c

    result_embed = discord.Embed(title="🎰 Tw Money Slots Result 🎰", color=msg_color)
    result_embed.description = f"{status_text}\n{reward_text}\n\n====== RESULT ======\n┃ {slot1} ┃ {slot2} ┃ {slot3} ┃"
    
    if slot1 == slot2 == slot3 == OWNER_PHOTO_EMOJI:
        result_embed.set_image(url="https://discordapp.com")

    await ctx.send(embed=result_embed)

# ==================== 💼 WORK COMMAND (Twork) ====================
@bot.command(name="Twork")
async def work(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    # បន្ថែមពាក្យ await រួចរាល់ដើម្បីបំបាត់ Warning ពណ៌លឿង
    if user_id in work_cooldown and not await bot.is_owner(ctx.author):
        remaining = work_cooldown[user_id] - asyncio.get_event_loop().time()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return await ctx.send(f"⏳ @{ctx.author.name}, you are tired! Please rest and try again in {minutes}m {seconds}s.")

    if user_id not in user_balances:
        user_balances[user_id] = 0

    earnings = random.randint(50, 200)
    user_balances[user_id] += earnings
    
    jobs = [
        "👷 You worked hard at a construction site",
        "👨‍🍳 You worked as a busy barista at a coffee shop",
        "🚗 You drove a delivery truck all day",
        "💻 You fixed system bugs as a programmer"
    ]
    random_job = random.choice(jobs)

    await ctx.send(f"💼 {random_job} and earned +{earnings} {custom_coin}!\n💰 Current Balance: {user_balances[user_id]} {custom_coin}")
    
    work_cooldown[user_id] = asyncio.get_event_loop().time() + 300

# ==================== 💰 BALANCE COMMAND (Twbal) ====================
@bot.command(name="Twbal")
async def balance(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    if user_id not in user_balances:
        user_balances[user_id] = 0
    await ctx.send(f"💰 @{ctx.author.name}'s Balance: {user_balances[user_id]} {custom_coin}")

# Start Server and Bot
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Error: DISCORD_TOKEN is missing!")
