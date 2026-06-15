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

# 🌟 គ្រាប់រង្វាន់ទាំង ៥
SLOTS_EMOJIS = ["💎", "👑", "🔥", "🍀", "🪙"]

# 🎬 ដាក់ Direct Link របស់ GIF នៅទីនេះ
URL_SPINNING_GIF = "https://media1.tenor.com/m/V1-T65pT7bEAAAAd/luck-777.gif"

user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} Slots Game is Ready!")

# ==================== 🎰 COMMANDS ====================

@bot.command()
async def Tw(ctx, bet: str):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id not in user_balances:
        user_balances[user_id] = 1000
        
    # ការគណនាចំនួនភ្នាល់
    if bet.lower() == "all":
        bet_amount = user_balances[user_id]
    else:
        try:
            bet_amount = int(bet)
        except ValueError:
            return await ctx.send("❌ Bet amount must be a number!")
            
    if bet_amount <= 0 or bet_amount > user_balances[user_id]:
        return await ctx.send(f"❌ Invalid amount! Your balance is {user_balances[user_id]}")

    # 🎬 ផ្ញើផ្ទាំង Embed កំពុងវិល
    embed_spinning = discord.Embed(
        title="🎀 ┃ TW SLOTS MACHINE 777 ┃ 🎀",
        description=f"🎰 ម៉ាស៊ីនកំពុងវិល... កំពុងអ៊ុតរង្វាន់!\n\n┃ 🪙 ប្រាក់ភ្នាល់: {bet_amount} {custom_coin}",
        color=0xffd700
    )
    embed_spinning.set_image(url=URL_SPINNING_GIF)
    spin_msg = await ctx.send(embed=embed_spinning)
    
    await asyncio.sleep(2) 

    # ==================== WIN / LOSE CALCULATION ====================
    final1, final2, final3 = random.choices(SLOTS_EMOJIS, k=3)

    if final1 == final2 == final3:
        win_amount = int(bet_amount * 10)
        user_balances[user_id] += win_amount
        result_comment = f"🎉 **JACKPOT! មហាសំណាងឈ្នះរង្វាន់ធំ!**\n💰 ទទួលបាន: +{win_amount} {custom_coin}"
    elif final1 == final2 or final2 == final3 or final1 == final3:
        win_amount = int(bet_amount * 2)
        user_balances[user_id] += win_amount
        result_comment = f"💵 **2-Match Combo!**\n💰 ទទួលបាន: +{win_amount} {custom_coin}"
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"❌ **You lost... សោកស្តាយផង!**\n📉 បាត់បង់: -{bet_amount} {custom_coin}"

    # 🎬 បង្ហាញលទ្ធផល
    final_layout = (
        f"**[ 🎰 លទ្ធផលម៉ាស៊ីនស្លត ]**\n"
        f"➡️ ┃ {final1} ┃ {final2} ┃ {final3} ┃ ⬅️\n\n"
        f"{result_comment}\n"
        f"💳 តុល្យភាពសរុប: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(title="🎀 ┃ TW SLOTS RESULT ┃ 🎀", description=final_layout, color=0xffd700)
    await spin_msg.edit(embed=result_embed)

@bot.command()
async def Twork(ctx):
    user_id = ctx.author.id
    current_time = time.time()
    if user_id in work_cooldown and work_cooldown[user_id] > current_time:
        return await ctx.send("⏳ You are tired! Please rest.")
    
    earnings = random.randint(50, 200)
    user_balances[user_id] = user_balances.get(user_id, 1000) + earnings
    work_cooldown[user_id] = current_time + 300
    await ctx.send(f"💼 Worked hard and earned +{earnings} Tw money!")

@bot.command()
async def Twbal(ctx):
    user_id = ctx.author.id
    await ctx.send(f"💰 Balance: {user_balances.get(user_id, 1000)} **Tw money**")

keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN: 
    bot.run(TOKEN)
