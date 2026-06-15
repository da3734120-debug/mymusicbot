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
bot = commands.Bot(command_prefix="!", intents=intents)

# 🌟 គ្រាប់រង្វាន់ទាំង ៥ របស់អ្នក (រៀបតាមតម្លៃ)
EMOJI_1 = "<:photooutput:1515974261599244338>"  # ថ្លៃបំផុត
EMOJI_2 = "<:IMG_8344:1516003344093548646>"
EMOJI_3 = "<:IMG_8343:1516004106412621924>"
EMOJI_4 = "<:IMG_8342:1516004432612163725>"
EMOJI_5 = "<:IMG_8350:1516004852130517073>"

EMOJI_VALUES = {EMOJI_1: 10, EMOJI_2: 7, EMOJI_3: 5, EMOJI_4: 3, EMOJI_5: 2}
SLOTS_EMOJIS = list(EMOJI_VALUES.keys())
user_balances = {}
work_cooldown = {} 

@bot.event
async def on_ready():
    print(f"🎰 {bot.user.name} with True Rolling Down Animation is Ready!")

# ==================== 🛠️ MESSAGE COMMAND HANDLER ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.strip()
    
    if content.startswith("Tw ") or content == "Tw" or content.lower() == "tw all":
        args = content.split()
        bet_val = args if len(args) > 1 else None
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

# ==================== 🎰 SLOTS LOGIC (ចលនាវិលរមៀលទម្លាក់ចុះក្រោម) ====================
async def play_slots_logic(ctx, bet: str = None):
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
            return await ctx.send("❌ Bet amount must be a number!")
            
    if bet_amount <= 0 or bet_amount > user_balances[user_id]:
        return await ctx.send(f"❌ Invalid amount or not enough money! Balance: {user_balances[user_id]} {custom_coin}")

    # ១. កំណត់លទ្ធផលឈ្នះចាញ់ពិតប្រាកដទុកជាមុន
    final1 = random.choice(SLOTS_EMOJIS)
    final2 = random.choice(SLOTS_EMOJIS)
    final3 = random.choice(SLOTS_EMOJIS)

    frame_title = "🎀 ┃ SLOTS MACHINE ┃ 🎀"

    # ២. បង្កើតទម្រង់ទូហ្គេម ៣ ជួរ (ជួរលើ, ជួរកណ្តាល, ជួរក្រោម) ដោយចាប់ផ្តើមពីរូបភាពចៃដន្យ
    row_top = [random.choice(SLOTS_EMOJIS) for _ in range(3)]
    row_mid = [random.choice(SLOTS_EMOJIS) for _ in range(3)]
    row_bot = [random.choice(SLOTS_EMOJIS) for _ in range(3)]

    # 🎬 ផ្ដើមផ្ញើសារដំបូង (Frame ទី ១)
    initial_text = (
        f"{frame_title}\n"
        f" ┌───⚙️───⚙️───⚙️───┐\n"
        f"  [ ⬛ {row_top[0]} ⬛ {row_top[1]} ⬛ {row_top[2]} ⬛ ]\n"
        f"▶ [ ⬛ {row_mid[0]} ⬛ {row_mid[1]} ⬛ {row_mid[2]} ⬛ ] 🌟\n"
        f"  [ ⬛ {row_bot[0]} ⬛ {row_bot[1]} ⬛ {row_bot[2]} ⬛ ]\n"
        f" └───🎰───🎰───🎰───┘\n"
        f"┃ bet 🪙 {bet_amount} ┃ spinning... 🎰"
    )
    spin_msg = await ctx.send(initial_text)
    await asyncio.sleep(0.35)

    # 🎬 ធ្វើការដេញកូដទម្លាក់រូបភាពចុះក្រោម (Frame ទី ២ ដល់ ទី ៤)
    for i in range(3):
        # ទាញរូបភាពជួរក្រោមចោល រួចយកជួរកណ្តាលមកជំនួសជួរក្រោម ហើយជួរលើមកជំនួសជួរកណ្តាល (ចលនាធ្លាក់ចុះពិតៗ)
        row_bot = row_mid.copy()
        row_mid = row_top.copy()
        # ប្រសិនបើជាជុំចុងក្រោយ គឺត្រូវរុញលទ្ធផលពិត (Final) ឱ្យរត់ចូលមកពីជួរលើបង្អស់
        if i == 2:
            row_top = [final1, final2, final3]
        else:
            row_top = [random.choice(SLOTS_EMOJIS) for _ in range(3)]

        rolling_text = (
            f"{frame_title}\n"
            f" ┌───⚙️───⚙️───⚙️───┐\n"
            f"  [ ⬛ {row_top[0]} ⬛ {row_top[1]} ⬛ {row_top[2]} ⬛ ] ⬇️\n"
            f"▶ [ ⬛ {row_mid[0]} ⬛ {row_mid[1]} ⬛ {row_mid[2]} ⬛ ] 🌟\n"
            f"  [ ⬛ {row_bot[0]} ⬛ {row_bot[1]} ⬛ {row_bot[2]} ⬛ ] ⬇️\n"
            f" └───🎰───🎰───🎰───┘\n"
            f"┃ bet 🪙 {bet_amount} ┃ rolling down... 🔄"
        )
        await spin_msg.edit(content=rolling_text)
        await asyncio.sleep(0.35) # ល្បឿនលឿនដែល Discord អនុញ្ញាត

    # ==================== WIN / LOSE CALCULATION ====================
    if final1 == final2 == final3:
        multiplier = EMOJI_VALUES[final1]
        win_amount = int(bet_amount * multiplier)
        user_balances[user_id] += win_amount
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

    # 🎬 ជុំចុងក្រោយបង្អស់: រុញលទ្ធផលពិត (Final) ចុះមកចំជួរកណ្តាល (ជួរឈ្នះផ្លូវការ) បេះបិទ
    row_bot = row_mid.copy()
    row_mid = [final1, final2, final3]
    row_top = [random.choice(SLOTS_EMOJIS) for _ in range(3)]

    final_layout = (
        f"{frame_title}\n"
        f" ┌───⚙️───⚙️───⚙️───┐\n"
        f"  [ ⬛ {row_top[0]} ⬛ {row_top[1]} ⬛ {row_top[2]} ⬛ ]\n"
        f"▶ [ ⬛ {row_mid[0]} ⬛ {row_mid[1]} ⬛ {row_mid[2]} ⬛ ] 👑\n"
        f"  [ ⬛ {row_bot[0]} ⬛ {row_bot[1]} ⬛ {row_bot[2]} ⬛ ]\n"
        f" └───🎰───🎰───🎰───┘\n"
        f"┃ {result_comment}\n"
        f"💰 Current Balance: {user_balances[user_id]} {custom_coin}"
    )
    
    result_embed = discord.Embed(description=final_layout, color=0xffd700)
    await spin_msg.edit(content="", embed=result_embed)

# ==================== 💼 WORK LOGIC ====================
async def work_logic(ctx):
    user_id = ctx.author.id
    custom_coin = "**Tw money**"
    if user_id in work_cooldown and work_cooldown[user_id] - asyncio.get_event_loop().time() > 0:
        return await ctx.send("⏳ You are tired! Please rest 5 minutes.")
        
    earnings = random.randint(50, 200)
    user_balances[user_id] = user_balances.get(user_id, 0) + earnings
    await ctx.send(f"💼 Worked hard and earned +{earnings} {custom_coin}!")
    work_cooldown[user_id] = asyncio.get_event_loop().time() + 300

# ==================== 💰 BALANCE LOGIC ====================
async def balance_logic(ctx):
    user_id = ctx.author.id
    await ctx.send(f"💰 Balance: {user_balances.get(user_id, 0)} **Tw money**")

keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN: bot.run(TOKEN)
