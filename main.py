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
    return "Tw Money Slots Game with Vertical Animation is Online!"

def run_web():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================== SETUP DISCORD BOT ====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="Tw", intents=intents)

# 🌟 គ្រាប់រង្វាន់ទាំង ៥ របស់អ្នក (រៀបតាមតម្លៃពីថ្លៃទៅថោក)
EMOJI_1 = "<:photooutput:1515974261599244338>"  # ថ្លៃបំផុត
EMOJI_2 = "<:IMG_8344:1516003344093548646>"
EMOJI_3 = "<:IMG_8343:1516004106412621924>"
EMOJI_4 = "<:IMG_8342:1516004432612163725>"
EMOJI_5 = "<:IMG_8350:1516004852130517073>"

# គុណតម្លៃរង្វាន់
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
    print(f"🎰 {bot.user.name} with Vertical Rolling is Ready!")

# ==================== 🎰 SLOTS COMMAND (Tw [bet]) ====================
@bot.command(name="")
async def play_slots(ctx, bet: str = None):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id not in user_balances:
        user_balances[user_id] = 0
        
    if bet is None:
        return await ctx.send(f"❌ Please enter a bet amount! Example: Tw 50 (Balance: {user_balances[user_id]} {custom_coin})")
    
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
        return await ctx.send(f"❌ You don't have enough money! Balance: {user_balances[user_id]} {custom_coin}")

    # កំណត់លទ្ធផលពិតប្រាកដទុកជាមុន
    final1 = random.choice(SLOTS_EMOJIS)
    final2 = random.choice(SLOTS_EMOJIS)
    final3 = random.choice(SLOTS_EMOJIS)

    # បង្កើតរូបភាពចៃដន្យសម្រាប់ធ្វើជា Frame បន្លំភ្នែកពេលវាកំពុងរត់ឡើងលើ
    rand1, rand2, rand3 = random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS)
    rand4, rand5, rand6 = random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS), random.choice(SLOTS_EMOJIS)

    frame_title = "🎀 ┃ SLOTS ┃ 🎀"

    # --- 🌟 ដំណាក់កាលចលនាវិលបញ្ឈរ (Vertical Rolling Animation) 🌟 ---
    
    # 🎬 Frame ទី ១: បង្ហាញរូបភាពដំបូង
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {rand1} ⬛ {rand2} ⬛ {rand3} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ spinning... 🎰"
    )
    spin_msg = await ctx.send(msg_text)
    await asyncio.sleep(0.4)

    # 🎬 Frame ទី ២: រុញរូបចាស់ឡើងលើ ជំនួសរូបថ្មីចូលពីក្រោម
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {rand4} ⬛ {rand5} ⬛ {rand6} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ rolling up... ⬆️"
    )
    await spin_msg.edit(content=msg_text)
    await asyncio.sleep(0.4)

    # 🎬 Frame ទី ៣: រុញឡើងលើម្តងទៀត ជិតដល់រូបពិតប្រាកដ
    msg_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {random.choice(SLOTS_EMOJIS)} ⬛ {random.choice(SLOTS_EMOJIS)} ⬛ {random.choice(SLOTS_EMOJIS)} ⬛ ]\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ stopping... 🎰"
    )
    await spin_msg.edit(content=msg_text)
    await asyncio.sleep(0.4)

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

    # 🎬 Frame ទី ៤ (លទ្ធផលចុងក្រោយ): រូបភាពឈប់ចំលទ្ធផលពិតប្រាកដ
    final_text = (
        f"{frame_title}\n"
        f"**[** ⬛ {final1} ⬛ {final2} ⬛ {final3} ⬛ ] **i'm**\n"
        f"┃          ┃ bet 🪙 {bet_amount}\n"
        f"┃          ┃ {result_comment}\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(description=final_text, color=0xffd700)
    
    # បើឈ្នះ Super Jackpot ឱ្យឡើងរូបភាពធំពីក្រោម
    if final1 == final2 == final3 == EMOJI_1:
        result_embed.set_image(url="https://discordapp.com")

    await spin_msg.edit(content="", embed=result_embed)

# ==================== 💼 WORK COMMAND (Twork) ====================
@bot.command(name="work")
async def work(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    
    if user_id in work_cooldown and not await bot.is_owner(ctx.author):
        remaining = work_cooldown[user_id] - asyncio.get_event_loop().time()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return await ctx.send(f"⏳ @{ctx.author.name}, please rest and try again in {minutes}m {seconds}s.")

    if user_id not in user_balances:
        user_balances[user_id] = 0

    earnings = random.randint(50, 200)
    user_balances[user_id] += earnings
    
    jobs = ["Constructed a building 👷", "Served coffee 👨‍🍳", "Delivered packages 🚗", "Fixed bugs 💻"]
    random_job = random.choice(jobs)

    await ctx.send(f"💼 {random_job} and earned +{earnings} {custom_coin}!\n💰 Current Balance: {user_balances[user_id]} {custom_coin}")
    work_cooldown[user_id] = asyncio.get_event_loop().time() + 300

# ==================== 💰 BALANCE COMMAND (Twbal) ====================
@bot.command(name="bal")
async def balance(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    if user_id not in user_balances:
        user_balances[user_id] = 0
    await ctx.send(f"💰 @{ctx.author.name}'s Balance: {user_balances[user_id]} {custom_coin}")

# Run Server and Bot
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Error: DISCORD_TOKEN is missing!")
