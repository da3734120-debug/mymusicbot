import discord
from discord.ext import commands
import random
import os
import asyncio
import time
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
bot = commands.Bot(command_prefix="!", intents=intents)

# 🌟 គ្រាប់រង្វាន់ទាំង ៥ របស់អ្នក (Custom Emojis)
EMOJI_1 = "<:photooutput:1515974261599244338>"  # ថ្លៃបំផុត
EMOJI_2 = "<:IMG_8344:1516003344093548646>"
EMOJI_3 = "<:IMG_8343:1516004106412621924>"
EMOJI_4 = "<:IMG_8342:1516004432612163725>"
EMOJI_5 = "<:IMG_8350:1516004852130517073>"

# 🔄 រូប GIF វិល 777 របស់អ្នក
SPINNING = "<a:jago33slotmachine:1516039385332715602>" 

EMOJI_VALUES = {EMOJI_1: 10, EMOJI_2: 7, EMOJI_3: 5, EMOJI_4: 3, EMOJI_5: 2}
SLOTS_EMOJIS = list(EMOJI_VALUES.keys())
user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} with Delayed Reels Stop is Ready!")

# ==================== 🛠️ MESSAGE COMMAND HANDLER ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    content = message.content.strip()
    args = content.split()
    
    if len(args) == 0:
        return

    # ឆែកពាក្យបញ្ជា "Tw"
    if args[0] == "Tw":
        bet_val = args[1] if len(args) > 1 else None
        ctx = await bot.get_context(message)
        await play_slots_logic(ctx, bet_val)
        return

    # ឆែកពាក្យបញ្ជា "Twork"
    if content == "Twork":
        ctx = await bot.get_context(message)
        await work_logic(ctx)
        return

    # ឆែកពាក្យបញ្ជា "Twbal"
    if content == "Twbal":
        ctx = await bot.get_context(message)
        await balance_logic(ctx)
        return

    await bot.process_commands(message)

# ==================== 🎰 SLOTS LOGIC (កែប្រែឱ្យបង្ហាញក្នុង Embed ទាំងអស់ដើម្បីបង្ការការគាំង) ====================
async def play_slots_logic(ctx, bet: str = None):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id not in user_balances:
        user_balances[user_id] = 1000
        
    if bet is None:
        return await ctx.send(f"❌ Please enter a bet amount! Example: `Tw 50`")
    
    if bet.lower() == "all":
        bet_amount = user_balances[user_id]
    else:
        try:
            bet_amount = int(bet)
        except ValueError:
            return await ctx.send("❌ Bet amount must be a number!")
            
    if bet_amount <= 0 or bet_amount > user_balances[user_id]:
        return await ctx.send(f"❌ Invalid amount or not enough money! Your balance is {user_balances[user_id]}")

    # កំណត់លទ្ធផលទុកជាមុន
    final1 = random.choice(SLOTS_EMOJIS)
    final2 = random.choice(SLOTS_EMOJIS)
    final3 = random.choice(SLOTS_EMOJIS)

    frame_title = "🎀 ┃ SLOTS MACHINE ┃ 🎀"

    # 🎬 ដំណាក់កាលទី ១: បង្ហាញរូបវិលទាំង ៣ ក្នុង Embed តែម្តង (វិធីនេះជួយឱ្យ Discord បង្ហាញរូបបានលឿន និងមិនគាំង)
    embed_1 = discord.Embed(
        title=frame_title,
        description=f"[ ⬛ {SPINNING} ⬛ {SPINNING} ⬛ {SPINNING} ⬛ ]\n┃          ┃ bet 🪙 {bet_amount}\n┃          ┃ spinning... 🎰",
        color=0xffd700
    )
    spin_msg = await ctx.send(embed=embed_1)
    await asyncio.sleep(1.2)

    # 🎬 ដំណាក់កាលទី ២: ប្រអប់ទី១ ឈប់
    embed_2 = discord.Embed(
        title=frame_title,
        description=f"[ ⬛ {final1} ⬛ {SPINNING} ⬛ {SPINNING} ⬛ ]\n┃          ┃ bet 🪙 {bet_amount}\n┃          ┃ rolling... 🔄",
        color=0xffd700
    )
    await spin_msg.edit(embed=embed_2)
    await asyncio.sleep(0.7)

    # 🎬 ដំណាក់កាលទី ៣: ប្រអប់ទី២ ឈប់
    embed_3 = discord.Embed(
        title=frame_title,
        description=f"[ ⬛ {final1} ⬛ {final2} ⬛ {SPINNING} ⬛ ]\n┃          ┃ bet 🪙 {bet_amount}\n┃          ┃ stopping soon... 🎰",
    color=0xffd700
    )
    await spin_msg.edit(embed=embed_3)
    await asyncio.sleep(0.7)

    # ==================== WIN / LOSE CALCULATION ====================
    if final1 == final2 == final3:
        multiplier = EMOJI_VALUES[final1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        result_comment = f"🎉 JACKPOT! +{win_amount} {custom_coin}"
    elif final1 == final2 or final2 == final3 or final1 == final3:
        matched = final2 if final2 == final3 or final1 == final2 else final1
        win_amount = int(bet_amount * (EMOJI_VALUES[matched] / 2))
        if win_amount < 1: win_amount = 1
        user_balances[user_id] += win_amount
        result_comment = f"💵 2-Match Combo! +{win_amount} {custom_coin}"
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"❌ You lost... (-{bet_amount} {custom_coin})"

    # 🎬 ដំណាក់កាលចុងក្រោយ៖ ឈប់ទាំងអស់ រួចបង្ហាញលទ្ធផល
    final_layout = (
        f"[ ⬛ {final1} ⬛ {final2} ⬛ {final3} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ {result_comment}\n\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(title=frame_title, description=final_layout, color=0xffd700)
    if final1 == final2 == final3 == EMOJI_1:
        result_embed.set_image(url="https://discordapp.com")

    await spin_msg.edit(embed=result_embed)

# ==================== 💼 WORK LOGIC ====================
async def work_logic(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    current_time = time.time()

    if user_id in work_cooldown and work_cooldown[user_id] > current_time:
        remaining = int(work_cooldown[user_id] - current_time)
        minutes = remaining // 60
        seconds = remaining % 60
        return await ctx.send(f"⏳ You are tired! Please rest {minutes}m {seconds}s.")
        
    earnings = random.randint(50, 200)
    user_balances[user_id] = user_balances.get(user_id, 0) + earnings
    await ctx.send(f"💼 Worked hard and earned +{earnings} {custom_coin}!")
    work_cooldown[user_id] = current_time + 300

# ==================== 💰 BALANCE LOGIC ====================
async def balance_logic(ctx):
    user_id = ctx.author.id
    if user_id not in user_balances:
        user_balances[user_id] = 1000
    await ctx.send(f"💰 Balance: {user_balances.get(user_id, 0)} **Tw money**")

keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN: 
    bot.run(TOKEN)
