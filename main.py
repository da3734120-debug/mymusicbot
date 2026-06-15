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

# លេខកូដរូបថត App Emoji របស់អ្នក
OWNER_PHOTO_EMOJI = "<:photooutput:1515974261599244338>"

# បញ្ជីគុណតម្លៃរង្វាន់
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
    print(f"🎰 {bot.user.name} Fast Scrolling Slots is Ready!")

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

    # រៀបចំលទ្ធផលពិតប្រាកដទុកជាមុន
    slot1 = random.choice(SLOTS_EMOJIS)
    slot2 = random.choice(SLOTS_EMOJIS)
    slot3 = random.choice(SLOTS_EMOJIS)

    frame_title = "🎐 ┃ SLOTS ┃ 🎐"
    
    # 🌟 ១. គំនូរជីវចលរត់ដូររូបភាពក្នុងល្បឿនលឿន (Fast Scrolling Phase)
    # ប្រព័ន្ធនឹងរត់ដូររូបភាពឆ្លាស់គ្នាយ៉ាងលឿន (asyncio.sleep ទាបបំផុត) ដើម្បីឱ្យឃើញរូបភាពទាំងអស់រត់កាត់
    for _ in range(4):
        msg_text = (
            f"{frame_title}\n"
            f"**[** ⬛ {random.choice(SLOTS_EMOJIS)} ⬛ {random.choice(SLOTS_EMOJIS)} ⬛ {random.choice(SLOTS_EMOJIS)} ] **i'm**\n"
            f"┃ ⬛ ⬛ ⬛ ┃ bet 🪙 {bet_amount}\n"
            f"┃ ⬛ ⬛ ⬛ ┃ and spinning... 🎰"
        )
        if _ == 0:
            spin_msg = await ctx.send(msg_text)
        else:
            await spin_msg.edit(content=msg_text)
        await asyncio.sleep(0.2) # ល្បឿនរត់លឿនញាប់

    # 🌟 ២. ចាប់ហ្វ្រាំងឈប់ចំរូបលទ្ធផលពិតម្តងមួយៗពីឆ្វេងទៅស្តាំ
    # ប្រអប់ទី ១ ឈប់
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {slot1} ⬛ {random.choice(SLOTS_EMOJIS)} ⬛ {random.choice(SLOTS_EMOJIS)} ] **i'm**\n"
        f"┃ ⬛ ⬛ ⬛ ┃ bet 🪙 {bet_amount}\n"
        f"┃ ⬛ ⬛ ⬛ ┃ and spinning... 🎰"
    )
    await spin_msg.edit(content=msg_text)
    await asyncio.sleep(0.4)
    
    # Presប្រអប់ទី ២ ឈប់
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {slot1} ⬛ {slot2} ⬛ {random.choice(SLOTS_EMOJIS)} ] **i'm**\n"
        f"┃ ⬛ ⬛ ⬛ ┃ bet 🪙 {bet_amount}\n"
        f"┃ ⬛ ⬛ ⬛ ┃ and spinning... 🎰"
    )
    await spin_msg.edit(content=msg_text)
    await asyncio.sleep(0.4)

    # ==================== WIN / LOSE CALCULATION ====================
    if slot1 == slot2 == slot3:
        multiplier = EMOJI_VALUES[slot1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        
        if slot1 == OWNER_PHOTO_EMOJI:
            result_comment = f"and won the SUPER JACKPOT! +{win_amount} {custom_coin} 👑"
        else:
            result_comment = f"and won the JACKPOT! +{win_amount} {custom_coin} 🎉"
        
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        matched_emoji = slot2 if slot2 == slot3 or slot1 == slot2 else slot1
        multiplier = EMOJI_VALUES[matched_emoji] / 2
        win_amount = int(bet_amount * multiplier)
        if win_amount < 1: win_amount = 1
        
        user_balances[user_id] += win_amount
        result_comment = f"and won a 2-Match Combo! +{win_amount} {custom_coin} 💵"
        
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"and won nothing... :c"

    # 🌟 ៣. បង្ហាញផ្ទាំងលទ្ធផលចុងក្រោយតាមរចនាបថជួរដេកផ្ដេក
    final_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {slot1} ⬛ {slot2} ⬛ {slot3} ] **i'm**\n"
        f"┃ ⬛ ⬛ ⬛ ┃ bet 🪙 {bet_amount}\n"
        f"┃ ⬛ ⬛ ⬛ ┃ {result_comment}\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    await spin_msg.edit(content=final_text)

# ==================== 💼 WORK COMMAND (Twork) ====================
@bot.command(name="Twork")
async def work(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
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
