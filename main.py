import discord
from discord.ext import commands
import asyncio
import os
import random
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Bot XO Online 24/7!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): Thread(target=run_web_server).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents, case_insensitive=True)

user_balances = {}
active_players = set()
emoji = "<:photooutput:1515974261599244338>"

def get_balance(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = {"wallet": 100, "bank": 0}
    return user_balances[user_id]

def draw_board(board):
    lines = []
    for i in range(0, 9, 3):
        lines.append(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    return "\n---------\n".join(lines)

def check_winner(b):
    for i in range(0, 9, 3):
        if b[i] == b[i+1] == b[i+2] != "⬜": return b[i]
    for i in range(3):
        if b[i] == b[i+3] == b[i+6] != "⬜": return b[i]
    if b[0] == b[4] == b[8] != "⬜": return b[0]
    if b[2] == b[4] == b[6] != "⬜": return b[2]
    if "⬜" not in b: return "Tie"
    return None

@bot.event
async def on_ready(): print(f'📢 Bot XO Online: {bot.user.name}')

@bot.command(name="tbal")
async def tbal(ctx):
    bal = get_balance(ctx.author.id)
    embed = discord.Embed(title=f"💳 គណនីរបស់ {ctx.author.name}", color=discord.Color.green())
    embed.add_field(name="👛 ក្នុងកាបូប (Wallet)", value=f"{bal['wallet']} {emoji}", inline=False)
    embed.add_field(name="🏦 ក្នុងធនាគារ (Bank)", value=f"{bal['bank']} {emoji}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="dep")
async def deposit(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["wallet"] < amt:
        await ctx.send("❌ លុយមិនត្រឹមត្រូវ ឬមិនគ្រប់គ្រាន់ទេ!")
        return
    bal["wallet"] -= amt
    bal["bank"] += amt
    await ctx.send(f"✅ បានដាក់លុយ {amt} {emoji} ចូលធនាគាររួចរាល់!")

@bot.command(name="with")
async def withdraw(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["bank"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["bank"] < amt:
        await ctx.send("❌ លុយមិនត្រឹមត្រូវ ឬមិនគ្រប់គ្រាន់ទេ!")
        return
    bal["bank"] -= amt
    bal["wallet"] += amt
    await ctx.send(f"✅ បានដកលុយ {amt} {emoji} មកកាបូបរួចរាល់!")

@bot.command(name="txo")
async def txo(ctx, p2: discord.Member, bet_amount: int):
    p1 = ctx.author
    if p1 == p2 or bet_amount <= 0:
        await ctx.send("❌ មិនអាចលេងបានទេ!")
        return
        
    if p1.id in active_players:
        await ctx.send(f"❌ {p1.mention} អ្នកកំពុងជាប់លេងហ្គេមមួយរួចហើយ! សូមលេងឱ្យចប់សិន!")
        return
    if p2.id in active_players:
        await ctx.send(f"❌ {p2.mention} កំពុងជាប់លេងហ្គេមជាមួយអ្នកផ្សេងរួចហើយ!")
        return

    p1_bal, p2_bal = get_balance(p1.id), get_balance(p2.id)
    if p1_bal["wallet"] < bet_amount or p2_bal["wallet"] < bet_amount:
        await ctx.send("❌ មានភាគីម្ខាងខ្វះលុយក្នុងកាបូប!")
        return

    await ctx.send(f"🎮 {p2.mention}! {p1.mention} បបួលលេង XO ភ្នាល់ {bet_amount} {emoji}!\n📌 **{p1.name}**=❌ | **{p2.name}**=⭕\nវាយពាក្យ accept ឬ decline (មានពេលឆ្លើយតប ៦០ វិនាទី)។")
    try:
        res = await bot.wait_for('message', check=lambda m: m.author == p2 and m.channel == ctx.channel and m.content.lower() in ['accept', 'decline'], timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send("⏰ ហួសពេលកំណត់ក្នុងការទទួលការបបួល!")
        return

    if res.content.lower() == 'decline':
        await ctx.send("❌ បានបដិសេធ!")
        return

    active_players.add(p1.id)
    active_players.add(p2.id)

    p1_bal["wallet"] -= bet_amount
    p2_bal["wallet"] -= bet_amount
    pot, match_num, turn, st_player = bet_amount * 2, 1, p1, p1

    try:
        while True:
            await ctx.send(f"⚔️ ប្រកួតទី {match_num}! (ក្អមកណ្តាល៖ {pot} {emoji})")
            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"វេនរបស់ {turn.mention} ({'❌' if turn == p1 else '⭕'}):\n```{draw_board(board)}```\n⏰ *មានពេល ៥ នាទីក្នុងការចុចដើរ កុំ AFK!*")
                try:
                    # កែប្រែត្រង់នេះ៖ ប្តូរ Timeout ពី 45.0 ទៅ 300.0 វិនាទី (៥ នាទី)
                    msg = await bot.wait_for('message', check=lambda m: m.author == turn and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg.content) - 1
                except asyncio.TimeoutError:
                    # ករណីអ្នកលេង AFK លើសពី ៥ នាទី
                    await ctx.send(f"⏰ {turn.mention} បាន AFK លើសពី ៥ នាទីមិនព្រមដៅសញ្ញា! ត្រូវបានកាត់សេចក្តីឱ្យចាញ់ភ្លាមៗ!")
                    win_sym = '⭕' if turn == p1 else '❌'
                    break
                if board[move] != "⬜": continue
                board[move] = '❌' if turn == p1 else '⭕'
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
                turn = p2 if turn == p1 else p1
            if tie:
                await ctx.send(f"🏁 ស្មើគ្នា!\n```{draw_board(board)}```\n🤝 លេងឡើងវិញភ្លាមៗ...")
                match_num += 1
                st_player = p2 if st_player == p1 else p1
                turn = st_player
                await asyncio.sleep(2)
                continue
            break

        winner = p1 if win_sym == '❌' else p2
        loser = p2 if winner == p1 else p1
        get_balance(winner.id)["wallet"] += pot
        await ctx.send(f"🏁 លទ្ធផលចុងក្រោយ:\n```{draw_board(board)}```\n🎉 {winner.mention} ឈ្នះបាន {pot} {emoji}!\n💸 {loser.mention} ចាញ់អស់ {bet_amount} {emoji}!")
    finally:
        active_players.discard(p1.id)
        active_players.discard(p2.id)

@bot.command(name="vsnpc")
async def vsnpc(ctx, bet_amount: int):
    p1 = ctx.author
    if bet_amount <= 0: return
    
    if p1.id in active_players:
        await ctx.send(f"❌ {p1.mention} អ្នកកំពុងជាប់លេងហ្គេមមួយរួចហើយ! សូមលេងឱ្យចប់សិន!")
        return

    p1_bal = get_balance(p1.id)
    if p1_bal["wallet"] < bet_amount:
        await ctx.send("❌ លុយក្នុងកាបូបមិនគ្រប់គ្រាន់ទេ!")
        return

    active_players.add(p1.id)

    await ctx.send(f"🤖 ហ្គេមទល់នឹង NPC ចាប់ផ្តើម! ភ្នាល់ {bet_amount} {emoji}\n📌 {p1.mention}=**❌** (ដើរមុន) | NPC**=**⭕ (ដើរក្រោយ)")
    p1_bal["wallet"] -= bet_amount
    pot, match_num = bet_amount * 2, 1

    try:
        while True:
            await ctx.send(f"⚔️ ប្រកួតទល់នឹង NPC ទី {match_num}! (ក្នុងក្អម៖ {pot} {emoji})")
            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"🟢 វេនរបស់ {p1.mention} (❌):\n```{draw_board(board)}```\n⏰ *មានពេល ៥ នាទីក្នុងការចុចដើរ!*")
                try:
                    # កែប្រែត្រង់នេះ៖ ប្តូរ Timeout សម្រាប់ vsnpc ទៅ ៥ នាទី (៣០០ វិនាទី) ដូចគ្នា
                    msg = await bot.wait_for('message', check=lambda m: m.author == p1 and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {p1.mention} ទុកចោលលើសពី ៥ នាទី! ហ្គេមត្រូវបានបញ្ចប់ ហើយ NPC ជាអ្នកឈ្នះ។")
                    win_sym = "⭕"
                    break
                if board[move] != "⬜": continue
                board[move] = "❌"
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break

                await asyncio.sleep(1.0)
                empty = [i for i, c in enumerate(board) if c == "⬜"]
                board[random.choice(empty)] = "⭕"
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
            if tie:
                await ctx.send(f"🏁 ស្មើគ្នាជាមួយ NPC!\n```{draw_board(board)}```\n🤝 លេងឡើងវិញភ្លាមៗ...")
                match_num += 1
                await asyncio.sleep(2)
                continue
            break

        await ctx.send(f"🏁 លទ្ធផលចុងក្រោយ:\n```{draw_board(board)}```")
        if win_sym == "❌":
            p1_bal["wallet"] += pot
            await ctx.send(f"🎉 {p1.mention} ឈ្នះ NPC បាន {pot} {emoji}!")
        else:
            await ctx.send(f"💸 {p1.mention} ចាញ់ NPC អស់ {bet_amount} {emoji}!")
    finally:
        active_players.discard(p1.id)

if name == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token: bot.run(token)
