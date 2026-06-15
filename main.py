import discord
from discord.ext import commands
import asyncio
import os
from flask import Flask
from threading import Thread

# --- ផ្នែកទី ១៖ បង្កើត Web Server សម្រាប់ការពារកុំឱ្យ Render ងងុយដេក (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot របស់អ្នកកំពុងដំណើរការ ២៤ ម៉ោង!"

def run_web_server():
    # ដំណើរការនៅលើ Port 10000 ឬ Port ដែល Render ផ្ដល់ឱ្យ
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# --- ផ្នែកទី ២៖ កូដហ្គេម XO ភ្នាល់លុយ ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

user_balances = {}

def draw_board(board):
    lines = []
    for i in range(0, 9, 3):
        lines.append(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    return "\n---------\n".join(lines)

def check_winner(b):
    win_states = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for state in win_states:
        if b[state[0]] == b[state[1]] == b[state[2]] and b[state[0]] != "⬜":
            return b[state[0]]
    if "⬜" not in b:
        return "Tie"
    return None

@bot.event
async def on_ready():
    print(f'Bot XO ដំណើរការដោយជោគជ័យ៖ {bot.user.name}')

@bot.command()
async def wallet(ctx):
    balance = user_balances.get(ctx.author.id, 100)
    user_balances[ctx.author.id] = balance
    await ctx.send(f"💰 {ctx.author.mention} មានលុយ៖ {balance} កាក់")

@bot.command()
async def xo(ctx, p2: discord.Member, bet_amount: int):
    p1 = ctx.author
    if p1 == p2:
        await ctx.send("❌ អ្នកមិនអាចលេងជាមួយខ្លួនឯងបានទេ!")
        return
    if bet_amount <= 0:
        await ctx.send("❌ ចំនួនលុយភ្នាល់ត្រូវតែធំជាង ០!")
        return

    p1_bal = user_balances.get(p1.id, 100)
    p2_bal = user_balances.get(p2.id, 100)
    user_balances[p1.id], user_balances[p2.id] = p1_bal, p2_bal

    if p1_bal < bet_amount or p2_bal < bet_amount:
        await ctx.send("❌ មានភាគីម្ខាងមិនមានលុយគ្រប់គ្រាន់សម្រាប់ភ្នាល់ទេ!")
        return

    await ctx.send(f"🎮 {p2.mention}! {p1.mention} បបួលលេង XO ភ្នាល់ {bet_amount} កាក់!\nវាយ !accept ដើម្បីព្រម ឬ !decline ដើម្បីបដិសេធ។")

    def check_accept(m):
        return m.author == p2 and m.channel == ctx.channel and m.content.lower() in ['!accept', '!decline']

    try:
        response = await bot.wait_for('message', check=check_accept, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send("⏰ ហ្គេមត្រូវបានលុបចោលដោយសារគ្មានការឆ្លើយតប។")
        return

    if response.content.lower() == '!decline':
        await ctx.send(f"❌ {p2.mention} បានបដិសេធ។")
        return

    user_balances[p1.id] -= bet_amount
    user_balances[p2.id] -= bet_amount
    total_pot = bet_amount * 2

    match_number = 1
    p1_symbol, p2_symbol = "❌", "⭕"
    starting_player = p1 

    while True:
        await ctx.send(f"⚔️ ចាប់ផ្តើមប្រកួតទី {match_number}! (លុយក្នុងក្អមសរុប៖ {total_pot} កាក់)")
        board = ["⬜"] * 9
        turn = starting_player
        game_ended_in_tie = False
        winner = None

        while True:
            current_board_str = draw_board(board)
            current_symbol = p1_symbol if turn == p1 else p2_symbol
            await ctx.send(f"វេនរបស់ {turn.mention} ({current_symbol}):\n```{current_board_str}```")

            def check_move(m):
                return m.author == turn and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9

            try:
                move_msg = await bot.wait_for('message', check=check_move, timeout=45.0)
                move = int(move_msg.content) - 1
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ {turn.mention} ហួសពេលកំណត់! ត្រូវបានកាត់សេចក្តីឱ្យចាញ់។")
                winner = p2 if turn == p1 else p1
                break

            if board[move] != "⬜":
                await ctx.send("❌ ឡូផ្លូវនោះមានគេដាក់រួចហើយ! ជ្រើសរើសលេខផ្សេង។")
                continue

            board[move] = current_symbol
            
            result = check_winner(board)if result:
                final_board_str = draw_board(board)
                await ctx.send(f"🏁 **លទ្ធផល៖**\n```{final_board_str}```")
                if result == "Tie":
                    game_ended_in_tie = True
                else:
                    winner = p1 if result == p1_symbol else p2
                break

            turn = p2 if turn == p1 else p1

        if game_ended_in_tie:
            await ctx.send("🤝 **ស្មើគ្នាហើយ! ហ្គេមនឹងចាប់ផ្តើមឡើងវិញភ្លាមៗ...**")
            match_number += 1
            starting_player = p2 if starting_player == p1 else p1
            await asyncio.sleep(2)
            continue

        break

    user_balances[winner.id] += total_pot
    loser = p2 if winner == p1 else p1

    await ctx.send(f"🎉 អបអរសាទរ! {winner.mention} ឈ្នះដាច់ជាស្ថាពរ និងទទួលបានកាក់ភ្នាល់ទាំងអស់សរុប {total_pot} កាក់! (សមតុល្យ៖ {user_balances[winner.id]})")
    await ctx.send(f"💸 {loser.mention} បានចាញ់ការប្រកួត (សមតុល្យនៅសល់៖ {user_balances[loser.id]})")

# --- ផ្នែកទី ៣៖ ដកស្រង់ Token ពី Render Environment Variable ហើយដំណើរការ Bot ---
if name == "__main__":
    keep_alive() # បើក Web Server ជំនួយ
    # ទាញយក Token ពី Environment Variable ដែលមានឈ្មោះថា DISCORD_TOKEN នៅលើ Render
    token = os.getenv('DISCORD_TOKEN') 
    if token:
        bot.run(token)
    else:
        print("❌ កំហុស៖ រកមិនឃើញ DISCORD_TOKEN នៅក្នុង Render បរិស្ថានឡើយ!")
