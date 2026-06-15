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
    return "Tw Money Slots Game with Official GIF Rolling is Online!"

def run_web():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================== SETUP DISCORD BOT ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 🌟 គ្រាប់រង្វាន់ទាំង ៥ របស់អ្នក (រៀបតាមតម្លៃ)
EMOJI_1 = "<:photooutput:1515974261599244338>"  # ថ្លៃបំផុត (Owner Photo)
EMOJI_2 = "<:IMG_8344:1516003344093548646>"
EMOJI_3 = "<:IMG_8343:1516004106412621924>"
EMOJI_4 = "<:IMG_8342:1516004432612163725>"
EMOJI_5 = "<:IMG_8350:1516004852130517073>"

# 🔄 កូដ Animated Emoji (GIF) វិល 777 ផ្លូវការរបស់អ្នក
SPINNING_EMOJI = "<a:jago33slotmachine:1516039385332715602>" 

EMOJI_VALUES = {EMOJI_1: 10, EMOJI_2: 7, EMOJI_3: 5, EMOJI_4: 3, EMOJI_5: 2}
SLOTS_EMOJIS = list(EMOJI_VALUES.keys())
user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} with Official GIF Rolling is Ready!")

# ==================== 🛠️ CUSTOM MESSAGE COMMAND HANDLER ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    args = content.split()
    
    # ឆែកមើល Command លេងស្លត (ឧទាហរណ៍៖ Tw 50 ឬ Tw all)
    if len(args) > 0 and args[0] == "Tw":
        bet_val = args[1] if len(args) > 1 else None
        ctx = await bot.get_context(message)
        await play_slots_logic(ctx, bet_val)
        return

    # ឆែកមើល Command ធ្វើការរកលុយ (Twork)
    if content == "Twork":
        ctx = await bot.get_context(message)
        await work_logic(ctx)
        return

    # ឆែកមើល Command មើលលុយ (Twbal)
    if content == "Twbal":
        ctx = await bot.get_context(message)
        await balance_logic(ctx)
        return

    await bot.process_commands(message)

# ==================== 🎰 SLOTS LOGIC (វិលរូប GIF រលូនដូចគេលេង) ====================
async def play_slots_logic(ctx, bet: str = None):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id not in user_balances:
        user_balances[user_id] = 1000  # ថែមលុយហ្វ្រី ១០០០ សម្រាប់អ្នកលេងដំបូង
        
    if bet is None:
        return await ctx.send(f"❌ Please enter a bet amount! Example: Tw 50 (Balance: {user_balances[user_id]} {custom_coin})")
    
    if bet.lower() == "all":
        bet_amount = user_balances[user_id]
    else:
        try:
            bet_amount = int(bet)
        except ValueError:
            return await ctx.send("❌ Bet amount must be a number or 'all'!")
            
    if bet_amount <= 0:
        return await ctx.send("❌ Bet amount must be greater than 0!")
        
    if bet_amount > user_balances[user_id]:
        return await ctx.send(f"❌ You don't have enough money! Balance: {user_balances[user_id]} {custom_coin} (Type Twork to earn money)")

    # ១. កំណត់លទ្ធផលពិតប្រាកដទុកជាមុន
    final1 = random.choice(SLOTS_EMOJIS)
    final2 = random.choice(SLOTS_EMOJIS)
    final3 = random.choice(SLOTS_EMOJIS)

    frame_title = "🎀 ┃ SLOTS MACHINE ┃ 🎀"

    # 🎬 ២. បង្ហាញរូប GIF វិល 777 លឿនស្លេវពេញភ្នែក (រលូនល្អឥតខ្ចោះ មិនគាំង)
    rolling_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {SPINNING_EMOJI} ⬛ {SPINNING_EMOJI} ⬛ {SPINNING_EMOJI} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ spinning fast... 🔄"
    )
    spin_msg = await ctx.send(rolling_text)
    
    # ទុកពេល ២.៥ វិនាទីឱ្យរូប GIF វិលរត់ពេញកម្លាំង
    await asyncio.sleep(2.5)

    # ==================== WIN / LOSE CALCULATION ====================
    if final1 == final2 == final3:
        multiplier = EMOJI_VALUES[final1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amountif final1 == EMOJI_1:
            result_comment = f"👑 and won the SUPER JACKPOT! +{win_amount} {custom_coin}"
        else:
            result_comment = f"🎉 and won the JACKPOT! +{win_amount} {custom_coin}"
        
    elif final1 == final2 or final2 == final3 or final1 == final3:
        matched = final2 if final2 == final3 or final1 == final2 else final1
        win_amount = int(bet_amount * (EMOJI_VALUES[matched] / 2))
        if win_amount < 1: win_amount = 1
        
        user_balances[user_id] += win_amount
        result_comment = f"💵 and won a 2-Match Combo! +{win_amount} {custom_coin}"
        
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"❌ and won nothing... :c (Lost -{bet_amount} {custom_coin})"

    # 🎬 ៣. លុបរូបភាពវិលចោល រួចលោតផ្ទាំង Embed បង្ហាញលទ្ធផលពិតភ្លាមៗ
    final_layout = (
        f"{frame_title}\n"
        f"**[** ⬛ {final1} ⬛ {final2} ⬛ {final3} ⬛ ] **i'm**\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ {result_comment}\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(description=final_layout, color=0xffd700)
    
    # បើឈ្នះ Super Jackpot ឱ្យឡើងរូបថតរបស់អ្នកធំពីក្រោម
    if final1 == final2 == final3 == EMOJI_1:
        result_embed.set_image(url="https://discordapp.com")

    await spin_msg.edit(content="", embed=result_embed)

# ==================== 💼 WORK LOGIC ====================
async def work_logic(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    if user_id in work_cooldown and work_cooldown[user_id] - asyncio.get_event_loop().time() > 0:
        remaining = work_cooldown[user_id] - asyncio.get_event_loop().time()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return await ctx.send(f"⏳ @{ctx.author.name}, you are tired! Please rest and try again in {minutes}m {seconds}s.")
        
    earnings = random.randint(50, 200)
    user_balances[user_id] = user_balances.get(user_id, 0) + earnings
    
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

keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN: 
    bot.run(TOKEN)
        
