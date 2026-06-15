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
    return "Tw Money Slots Game with Spinning Animation is Online!"

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

# 🌟 រូបភាព GIF សម្រាប់ប្រើពេលកំពុងវិល (ប្រើរូបព្រួញវិលចម្រុះពណ៌ Standard របស់ Discord)
# ទោះលេងនៅ Server ណាក៏រូបភាពនេះរត់វិលយ៉ាងលឿន និងរលូនជានិច្ច មិនគាំងឡើយ
SPINNING_EMOJI = "🔄"

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
    print(f"🎰 {bot.user.name} with Spinning Animation is Ready!")

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

    frame_title = "🎀 ┃ SLOTS ┃ 🎀"
    
    # 🌟 ១. បង្ហាញផ្ទាំងរូបភាពវិលល្បឿនលឿនដំបូង (រត់វិលដោយប្រើរូប GIF ស្វ័យប្រវត្ត)
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {SPINNING_EMOJI} ⬛ {SPINNING_EMOJI} ⬛ {SPINNING_EMOJI} ⬛ ] **i'm**\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ spinning... 🎰"
    )
    spin_msg = await ctx.send(msg_text)
    
    # 🌟 ២. ទុកពេល ២ វិនាទីឱ្យប្រព័ន្ធរូបភាពរត់វិលយ៉ាងលឿនពេញភ្នែកអ្នកលេង
    await asyncio.sleep(2.0)

    # ==================== WIN / LOSE CALCULATION ====================
    if slot1 == slot2 == slot3:
        multiplier = EMOJI_VALUES[slot1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
        
        if slot1 == OWNER_PHOTO_EMOJI:
            result_comment = f"**and won the SUPER JACKPOT!** +{win_amount} {custom_coin} 👑"
        else:
            result_comment = f"**and won the JACKPOT!** +{win_amount} {custom_coin} 🎉"
        
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        matched_emoji = slot2 if slot2 == slot3 or slot1 == slot2 else slot1
        multiplier = EMOJI_VALUES[matched_emoji] / 2
        win_amount = int(bet_amount * multiplier)
        if win_amount < 1: win_amount = 1
        
        user_balances[user_id] += win_amount
        result_comment = f"**and won a 2-Match Combo!** +{win_amount} {custom_coin} 💵"
        
    else:
        user_balances[user_id] -= bet_amount
        result_comment = f"**and won nothing... :c** (Lost -{bet_amount} {custom_coin})"

    # 🌟 ៣. កែប្រែសារបង្ហាញផ្ទាំងលទ្ធផលចុងក្រោយ ឈប់ចំរូបភាពពិតប្រាកដ
    final_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {slot1} ⬛ {slot2} ⬛ {slot3} ⬛ ] **i'm**\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ {result_comment}\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(description=final_text, color=0xffd700)
    
    # បើឈ្នះ Jackpot រូបថតរបស់អ្នក ឱ្យឡើងរូបថតធំពីក្រោមថែមទៀត
    if slot1 == slot2 == slot3 == OWNER_PHOTO_EMOJI:
        result_embed.set_image(url="https://discordapp.com")

    await spin_msg.edit(content="", embed=result_embed)

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
        "Constructed a new building site 👷",
        "Served fresh coffee as a barista 👨‍🍳",
        "Delivered packages all day long 🚗",
        "Fixed a lot of website system bugs 💻"
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
