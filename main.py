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

# 🌟 គ្រាប់រង្វាន់ទាំង ៥ របស់អ្នកពេលឈប់ (ប្រើឈ្មោះច្បាស់ៗដើម្បីកុំឱ្យខុសសិទ្ធិ Role)
EMOJI_1 = "💎 DIAMOND"  # ថ្លៃបំផុត
EMOJI_2 = "👑 CROWN"
EMOJI_3 = "🔥 FIRE"
EMOJI_4 = "🍀 CLOVER"
EMOJI_5 = "🪙 COIN"

SLOTS_EMOJIS = [EMOJI_1, EMOJI_2, EMOJI_3, EMOJI_4, EMOJI_5]

# 🔥 លីងរូបភាព GIF វិលញាប់ៗបែប OwO Bot (ជាហ្វាយ GIF មានចលនាពិតប្រាកដ រត់រលូន ១០០%)
URL_SPINNING_GIF = "https://giphy.com"

user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} Slots Game (OwO Style) is Ready!")

# ==================== 🛠️ MESSAGE COMMAND HANDLER ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    content = message.content.strip()
    args = content.split()
    
    if len(args) == 0:
        return

    # ឆែកពាក្យបញ្ជា "Tw" ឱ្យដំណើរការភ្លាមៗ
    if args[0] == "Tw":
        bet_val = args[1] if len(args) > 1 else None
        ctx = await bot.get_context(message)
        await play_slots_logic(ctx, bet_val)
        return

    if content == "Twork":
        ctx = await bot.get_context(message)
        await work_logic(ctx)
        return

    if content == "Twbal":
        ctx = await bot.get_context(message)
        await balance_logic(ctx)
        return

    await bot.process_commands(message)

# ==================== 🎰 SLOTS LOGIC (OwO Bot Style) ====================
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

    frame_title = "🎀 ┃ TW SLOTS MACHINE 777 ┃ 🎀"

    # 🎬 ដំណាក់កាលទី ១៖ ផ្ញើផ្ទាំង Embed រូបភាព GIF វិលកញ្ជ្រោលភ្លាមៗ (ដូច OwO Bot ធ្វើ)
    embed_spinning = discord.Embed(
        title=frame_title,
        description=f"🎰 ម៉ាស៊ីនកំពុងវិលយ៉ាងញាប់... កំពុងអ៊ុតរកគ្រាប់រង្វាន់! 🎰\n\n┃ 🪙 ប្រាក់ភ្នាល់: {bet_amount} {custom_coin}",
        color=0xffd700
    )
    # បង្ខំឱ្យរូបភាព GIF បង្ហាញពេញអេក្រង់ Embed
    embed_spinning.set_image(url=URL_SPINNING_GIF)
    
    spin_msg = await ctx.send(embed=embed_spinning)
    
    # ទុកពេលឱ្យរូប GIF វិលចុះឡើងចំនួន ២.៥ វិនាទីពេញ ដើម្បីឱ្យអ្នកលេងមើលឃើញចលនាវិលញាប់ៗ
    await asyncio.sleep(2.5) 

    # ==================== WIN / LOSE CALCULATION ====================
    final1 = random.choice(SLOTS_EMOJIS)
    final2 = random.choice(SLOTS_EMOJIS)
    final3 = random.choice(SLOTS_EMOJIS)

    if final1 == final2 == final3:
        win_amount = int(bet_amount * 10)
        user_balances[user_id] += win_amount
        result_comment = f"🎉 **JACKPOT! មហាសំណាងឈ្នះរង្វាន់ធំមហិមា!**\n💰 ទទួលបាន: +{win_amount} {custom_coin}"
    elif final1 == final2 or final2 == final3 or final1 == final3:
        win_amount = int(bet_amount * 2)
        user_balances[user_id] += win_amount
        result_comment = f"💵 **2-Match Combo! (ត្រូវចំទម្រង់ ២ គ្រាប់)**\n💰 ទទួលបាន: +{win_amount} {custom_coin}"
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"❌ **You lost... សោកស្តាយផងបង លទ្ធផលមិនស៊ីគ្នាទេ!**\n📉 បាត់បង់: -{bet_amount} {custom_coin}"

    # 🎬 ដំណាក់កាលទី ២៖ ប្តូរផ្ទាំង Embed ទៅជាលទ្ធផលគ្រាប់រង្វាន់ច្បាស់ៗក្រឡែត
    final_layout = (
        f"**[ 🎰 លទ្ធផលម៉ាស៊ីនស្លត ]**\n"
        f"➡️ ┃ {final1} ┃ {final2} ┃ {final3} ┃ ⬅️\n\n"
        f"{result_comment}\n"
        f"💳 តុល្យភាពលុយសរុបបច្ចុប្បន្ន:  {user_balances[user_id]}  {custom_coin}"
    )
    
    result_embed = discord.Embed(title=frame_title, description=final_layout, color=0xffd700)
    
    # បើត្រូវ Jackpot ដាក់រូបភាព GIF អបអរសាទរធ្លាក់លុយបន្ថែម
    if final1 == final2 == final3:
        result_embed.set_image(url="https://giphy.com")

    # កែប្រែផ្ទាំង Embed ចាស់ទៅជាលទ្ធផលចុងក្រោយភ្លាមៗ
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
