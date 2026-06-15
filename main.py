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

# 🌟 កែប្រែ៖ ប្រើប្រាស់លីងរូបភាពទំហំតូចប៉ុន Emoji ដើម្បីឱ្យវាបង្ហាញរូបថតរបស់អ្នកក្នុងជួរលទ្ធផលផ្ទាល់
OWNER_PHOTO_LINK = "https://discordapp.com"

# បញ្ជីគុណតម្លៃរង្វាន់
EMOJI_VALUES = {
    OWNER_PHOTO_LINK: 10,  # JACKPOT GRAND PRIZE (រូបថតរបស់អ្នក គុណនឹង ១០)
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

    # Spinning Animation
    embed = discord.Embed(title="🎰 Tw Money Slots Machine 🎰", color=0xffd700)
    embed.add_field(name="====== SPINNING ======", value="┃ 🟩 ┃ 🟩 ┃ 🟩 ┃", inline=False)
    embed.description = f"@{ctx.author.name} is betting: {bet_amount} {custom_coin}..."
    spin_msg = await ctx.send(embed=embed)
    
    slot1 = random.choice(SLOTS_EMOJIS)
    slot2 = random.choice(SLOTS_EMOJIS)
    slot3 = random.choice(SLOTS_EMOJIS)
    
    await asyncio.sleep(0.7)
    embed.set_field_at(0, name="====== SPINNING ======", value=f"┃ {slot1} ┃ 🟩 ┃ 🟩 ┃", inline=False)
    await spin_msg.edit(embed=embed)
    
    await asyncio.sleep(0.7)
    embed.set_field_at(0, name="====== SPINNING ======", value=f"┃ {slot1} ┃ {slot2} ┃ 🟩 ┃", inline=False)
    await spin_msg.edit(embed=embed)
    
    await asyncio.sleep(0.7)
    
    # ==================== WIN / LOSE CALCULATION ====================
    result_embed = discord.Embed(title="🎰 Tw Money Slots Result 🎰")
    result_embed.add_field(name="====== RESULT ======", value=f"┃ {slot1} ┃ {slot2} ┃ {slot3} ┃", inline=False)
    
    # Case 1: 3 Match (Jackpot!)
    if slot1 == slot2 == slot3:
        multiplier = EMOJI_VALUES[slot1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        
        if slot1 == OWNER_PHOTO_LINK:
            result_embed.description = f"🌟 SUPER JACKPOT (BOT OWNER)! 🌟\nYou won the grand prize from the Bot Owner's photo!\n💵 Received: +{win_amount} {custom_coin}\n💰 Total: {user_balances[user_id]} {custom_coin}"
            result_embed.set_image(url="https://discordapp.com") # បង្ហាញរូបរបស់អ្នកធំពេញអេក្រង់តែម្តងពេលឈ្នះ Jackpot
        else:
            result_embed.description = f"🎉 JACKPOT! YOU WIN! 🎉\n💵 Received: +{win_amount} {custom_coin}\n💰 Total: {user_balances[user_id]} {custom_coin}"
        result_embed.color = 0x00ff00
        
    # Case 2: 2 Match
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        matched_emoji = slot2 if slot2 == slot3 or slot1 == slot2 else slot1
        multiplier = EMOJI_VALUES[matched_emoji] / 2
        win_amount = int(bet_amount * multiplier)
        if win_amount < 1: win_amount = 1
        
        user_balances[user_id] += win_amount
        result_embed.description = f"💵 2 MATCH VALUE! 💵\n💵 Received: +{win_amount} {custom_coin}\n💰 Total: {user_balances[user_id]} {custom_coin}"
        result_embed.color = 0x3498db
        
    # Case 3: Lose
    else:
        user_balances[user_id] -= bet_amount
        result_embed.description = f"❌ YOU LOSE! ❌\n📉 Lost: -{bet_amount} {custom_coin}\n💰 Balance: {user_balances[user_id]} {custom_coin}"
        result_embed.color = 0xe74c3c

    await spin_msg.edit(embed=result_embed)

# ==================== 💼 WORK COMMAND (Twork) ====================
@bot.command(name="Twork")
async def work(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id in work_cooldown and not bot.is_owner(ctx.author):
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
