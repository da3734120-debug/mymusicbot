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
    return "Tw Money Slots Game is Online!"

def run_web():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================== SETUP DISCORD BOT ====================
intents = discord.Intents.default()
intents.message_content = True

# 💡 កំណត់ Prefix ទៅជាសញ្ញាណាដែលប្លែក (ដូចជា !) ដើម្បីកុំឱ្យជាន់គ្នា ព្រោះយើងនឹងប្រើ on_message មកដោះស្រាយវិញ
bot = commands.Bot(command_prefix="!", intents=intents)

# 🌟 គ្រាប់រង្វាន់ទាំង ៥ របស់អ្នក
EMOJI_1 = "<:photooutput:1515974261599244338>"  # ថ្លៃបំផុត
EMOJI_2 = "<:IMG_8344:1516003344093548646>"
EMOJI_3 = "<:IMG_8343:1516004106412621924>"
EMOJI_4 = "<:IMG_8342:1516004432612163725>"
EMOJI_5 = "<:IMG_8350:1516004852130517073>"

EMOJI_VALUES = {
    EMOJI_1: 10,
    EMOJI_2: 7,
    EMOJI_3: 5,
    EMOJI_4: 3,
    EMOJI_5: 2
}

SLOTS_EMOJIS = list(EMOJI_VALUES.keys())
user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} is successfully configured and Ready!")

# ==================== 🛠️ CUSTOM MESSAGE COMMAND HANDLER ====================
# មុខងារនេះជួយចាប់រាល់ពាក្យបញ្ជាវាយ "Tw", "Twork", "Twbal" កុំឱ្យមាន Error លើ Terminal ទៀត
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    
    # 1. ឆែកមើលពាក្យបញ្ជាលេងស្លត (ឧទាហរណ៍៖ Tw 50 ឬ Tw all)
    if content.startswith("Tw ") or content == "Tw" or content.lower() == "tw all":
        args = content.split()
        bet_val = args[1] if len(args) > 1 else None
        ctx = await bot.get_context(message)
        await play_slots_logic(ctx, bet_val)
        return

    # 2. ឆែកមើលពាក្យបញ្ជាធ្វើការ (Twork)
    if content == "Twork":
        ctx = await bot.get_context(message)
        await work_logic(ctx)
        return

    # 3. ឆែកមើលពាក្យបញ្ជាមើលលុយ (Twbal)
    if content == "Twbal":
        ctx = await bot.get_context(message)
        await balance_logic(ctx)
        return

    await bot.process_commands(message)

# ==================== 🎰 SLOTS LOGIC ====================
async def play_slots_logic(ctx, bet: str = None):
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

    # រៀបចំលទ្ធផលទុកជាមុន
    final1 = random.choice(SLOTS_EMOJIS)
    final2 = random.choice(SLOTS_EMOJIS)
    final3 = random.choice(SLOTS_EMOJIS)

    # បង្កើតរូបភាពចៃដន្យសម្រាប់ចលនាវិលបញ្ឈរ Frame-by-Frame
    r1, r2, r3 = random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS)
    r4, r5, r6 = random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS)

    frame_title = "🎀 ┃ SLOTS ┃ 🎀"

    # Frame ទី ១
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {r1} ⬛ {r2} ⬛ {r3} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ spinning... 🎰"
    )
    spin_msg = await ctx.send(msg_text)
    await asyncio.sleep(0.5)

    # Frame ទី ២ (រត់ឡើងលើ)
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {r4} ⬛ {r5} ⬛ {r6} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ rolling up... ⬆️"
    )
    await spin_msg.edit(content=msg_text)
    await asyncio.sleep(0.5)

    # ==================== WIN / LOSE CALCULATION ====================
    if final1 == final2 == final3:
        multiplier = EMOJI_VALUES[final1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        
        if final1 == EMOJI_1:
            result_comment = f"**and won the SUPER JACKPOT!** +{win_amount} {custom_coin} 👑"
        else:
            result_comment = f"**and won the JACKPOT!** +{win_amount} {custom_coin} 🎉"
        
    elif final1 == final2 or final2 == final3 or final1 == final3:
        matched = final2 if final2 == final3 or final1 == final2 else final1
        multiplier = EMOJI_VALUES[matched] / 2
        win_amount = int(bet_amount * multiplier)
        if win_amount < 1: win_amount = 1
        
        user_balances[user_id] += win_amount
        result_comment = f"**and won a 2-Match Combo!** +{win_amount} {custom_coin} 💵"
        
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"**and won nothing... :c** (Lost -{bet_amount} {custom_coin})"

    # Frame ទី ៣: បង្ហាញលទ្ធផលចុងក្រោយឈប់ចំរូបភាពពិតប្រាកដ
    final_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {final1} ⬛ {final2} ⬛ {final3} ⬛ ] **i'm**\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ {result_comment}\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(description=final_text, color=0xffd700)
    
    if final1 == final2 == final3 == EMOJI_1:
        result_embed.set_image(url="https://discordapp.com")

    await spin_msg.edit(content="", embed=result_embed)

# ==================== 💼 WORK LOGIC ====================
async def work_logic(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id in work_cooldown:
        remaining = work_cooldown[user_id] - asyncio.get_event_loop().time()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return await ctx.send(f"⏳ @{ctx.author.name}, you are tired! Please rest and try again in {minutes}m {seconds}s.")

    if user_id not in user_balances:
        user_balances[user_id] = 0

    earnings = random.randint(50, 200)
    user_balances[user_id] += earnings
    
    jobs = ["Constructed a building 👷", "Served coffee 👨‍🍳", "Delivered packages 🚗", "Fixed bugs 💻"]
    random_job = random.choice(jobs)

    await ctx.send(f"💼 {random_job} and earned +{earnings} {custom_coin}!\n💰 Current Balance: {user_balances[user_id]} {custom_coin}")
    work_cooldown[user_id] = asyncio.get_event_loop().time() + 300

# ==================== 💰 BALANCE LOGIC ====================
async def balance_logic(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    if user_id not in user_balances:
        user_balances[user_id] = 0
    await ctx.send(f"💰 @{ctx.author.name}'s Balance: {user_balances[user_id]} {custom_coin}")

# Start Web Server and Bot
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Error: DISCORD_TOKEN is missing!")
