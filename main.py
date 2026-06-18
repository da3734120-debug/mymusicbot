import discord
from discord.ext import commands, tasks
import asyncio
import os
import random
import json
from flask import Flask
from threading import Thread

# ==================== Web Server ====================
app = Flask('')

@app.route('/')
def home(): 
    return "Bot XO Online 24/7!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): 
    Thread(target=run_web_server).start()

# ==================== Database Setup ====================
DATA_FILE = "/data/balances.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(user_balances, f, indent=4)

# ==================== Utilities ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

user_balances = load_data()
active_players = set()

@tasks.loop(minutes=5.0)
async def auto_save_backup():
    save_data()
    print("💾 [Auto-Save] Balances backed up successfully!")

emoji = "<:emoji_5:1516480628370047250>" 
game_icon = "🎮"

def format_number(num):
    return "{:,}".format(num)

def get_balance(user_id):
    uid = str(user_id)
    if uid not in user_balances:
        user_balances[uid] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0}
        save_data()
    if "win" not in user_balances[uid]:
        user_balances[uid]["win"] = 0
        user_balances[uid]["lost"] = 0
        save_data()
    return user_balances[uid]

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

# 🧠 ប្រព័ន្ធខួរក្បាល AI Smart NPC ឆ្លាតវៃ (Block & Win Logic)
def get_npc_move(board):
    empty_spots = [i for i, c in enumerate(board) if c == "⬜"]
    
    # ១. រកផ្លូវវាយសម្រុកដើម្បីឈ្នះ (បើ NPC ជិតបាន ៣ គ្រាប់)
    for spot in empty_spots:
        test_board = board.copy()
        test_board[spot] = "⭕"
        if check_winner(test_board) == "⭕":
            return spot

    # ២. រកផ្លូវស្ទាក់បិទផ្លូវអ្នកលេង (បើអ្នកលេងជិតបាន ៣ គ្រាប់)
    for spot in empty_spots:
        test_board = board.copy()
        test_board[spot] = "❌"
        if check_winner(test_board) == "❌":
            return spot

    # ៣. យុទ្ធសាស្ត្រល្អបំផុត៖ វាយយកប្រអប់កណ្តាល (លេខ ៥)
    if 4 in empty_spots:
        return 4

    # ៤. វាយលុកយកប្រអប់ជ្រុង (១, ៣, ៧, ៩)
    corners = [i for i in [0, 2, 6, 8] if i in empty_spots]
    if corners:
        return random.choice(corners)

    # ៥. ចុចជ្រើសរើសកន្លែងធម្មតាដែលនៅសល់
    return random.choice(empty_spots)

@bot.event
async def on_ready(): 
    print(f'📢 Bot XO Online: {bot.user.name}')
    auto_save_backup.start()
    # ==================== Economy Commands ====================
@bot.command(name="tbal")
async def tbal(ctx):
    bal = get_balance(ctx.author.id)
    embed = discord.Embed(title=f"💳 {ctx.author.display_name}'s Profile", color=discord.Color.blue())
    embed.description = (
        f"**Coins :** {format_number(bal['wallet'])} {emoji}\n**Bank :** {format_number(bal['bank'])} {emoji}\n\n"
        f"📊 Gameplay Statistics**\n**Lost : {bal['lost']} times\n**Win :** {bal['win']} times"
    )
    if ctx.author.avatar: 
        embed.set_thumbnail(url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="Tbank")
async def deposit(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["wallet"] < amt:
        await ctx.send("❌ Invalid amount or insufficient coins!")
        return
    bal["wallet"] -= amt
    bal["bank"] += amt
    save_data()
    await ctx.send(f"🏦 Deposited +{format_number(amt)} {emoji} into Bank.")

@bot.command(name="Tout")
async def withdraw(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["bank"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["bank"] < amt:
        await ctx.send("❌ Invalid amount or insufficient coins in bank!")
        return
    bal["bank"] -= amt
    bal["wallet"] += amt
    save_data()
    await ctx.send(f"💸 Withdrew +{format_number(amt)} {emoji} to Wallet.")

@bot.command(name="tp")
async def transfer_money(ctx, receiver: discord.Member, amount: int):
    sender = ctx.author
    if sender.id == receiver.id or amount <= 0:
        await ctx.send("❌ Invalid transfer action!")
        return
    s_bal = get_balance(sender.id)
    r_bal = get_balance(receiver.id)
    if s_bal["wallet"] < amount:
        await ctx.send("❌ Insufficient coins!")
        return

    embed_tp = discord.Embed(title="💸 Confirm Transfer", description=f"Transfer {format_number(amount)} {emoji} to {receiver.mention}?", color=discord.Color.gold())
    view = QuickButtonView(allowed_user=sender)
    msg = await ctx.send(embed=embed_tp, view=view)
    await view.wait()

    for child in view.children: 
        child.disabled = True
        
    if view.value == "accept":
        s_bal["wallet"] -= amount
        r_bal["wallet"] += amount
        save_data()
        embed_tp.title = "✅ Transfer Completed"
        embed_tp.color = discord.Color.green()
    else:
        embed_tp.title = "❌ Transfer Cancelled"
        embed_tp.color = discord.Color.red()
    await msg.edit(embed=embed_tp, view=view)

# ==================== UI View Components ====================
class QuickButtonView(discord.ui.View):
    def __init__(self, allowed_user, timeout=60.0):
        super().__init__(timeout=timeout)
        self.allowed_user = allowed_user
        self.value = None

    async def handle_click(self, interaction: discord.Interaction, value: str):
        if interaction.user.id != self.allowed_user.id:
            await interaction.response.send_message("❌ You are not allowed to use this button!", ephemeral=True)
            return
        self.value = value
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Accept ✅", style=discord.ButtonStyle.green)
    async def accept_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "accept")

    @discord.ui.button(label="Decline ❌", style=discord.ButtonStyle.red)
    async def decline_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "decline")
        # ==================== Game Commands (Player vs Player) ====================
@bot.command(name="txo")
async def txo(ctx, p2: discord.Member, bet_amount: int):
    p1 = ctx.author
    if p1.id == p2.id or bet_amount <= 0 or p1.id in active_players or p2.id in active_players:
        await ctx.send("❌ Game cannot start! Invalid match config or player busy.")
        return
    p1_bal, p2_bal = get_balance(p1.id), get_balance(p2.id)
    if p1_bal["wallet"] < bet_amount or p2_bal["wallet"] < bet_amount:
        await ctx.send("❌ Insufficient coins!")
        return

    view = QuickButtonView(allowed_user=p2)
    msg = await ctx.send(f"🎮 {p2.mention}, {p1.mention} challenges you to XO for {format_number(bet_amount)} {emoji}!", view=view)
    await view.wait()

    for child in view.children: 
        child.disabled = True
        
    if view.value != "accept":
        await msg.edit(content="❌ Challenge declined or expired!", view=view)
        return

    active_players.add(p1.id)
    active_players.add(p2.id)
    p1_bal["wallet"] -= bet_amount
    p2_bal["wallet"] -= bet_amount
    save_data()
    
    pot = bet_amount * 2
    match_num, turn, st_player = 1, p1, p1

    try:
        while True:
            await ctx.send(f"⚔️ **Match 1vs1 Active - Round #{match_num} (Pool: {format_number(pot)} {emoji})**")
            board, tie, win_sym = ["⬜"] * 9, False, None
            board_msg = await ctx.send(f"{turn.mention}'s turn:\n```\n{draw_board(board)}\n```")

            while True:
                try:
                    m = await bot.wait_for('message', check=lambda m: m.author.id == turn.id and m.channel.id == ctx.channel.id and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(m.content) - 1
                    try: await m.delete()
                    except: pass
                except asyncio.TimeoutError:
                    win_sym = '⭕' if turn == p1 else '❌'
                    break

                if board[move] != "⬜": 
                    continue
                board[move] = '❌' if turn == p1 else '⭕'
                
                res = check_winner(board)
                if res:
                    if res == "Tie": 
                        tie = True
                    else: 
                        win_sym = res
                    break
                turn = p2 if turn == p1 else p1
                await board_msg.edit(content=f"{turn.mention}'s turn:\n```\n{draw_board(board)}\n```")
                
            if tie:
                await ctx.send(f"🤝 Tie! Rematching...\n```\n{draw_board(board)}\n```")
                match_num += 1
                st_player = p2 if st_player == p1 else p1
                turn = st_player
                continue
            break

        winner = p1 if win_sym == '❌' else p2
        loser = p2 if winner == p1 else p1
        user_balances[str(winner.id)]["wallet"] += pot
        user_balances[str(winner.id)]["win"] += 1
        user_balances[str(loser.id)]["lost"] += 1
        save_data()
        await ctx.send(f"👑 **{winner.mention} WON THE MATCH AND CLAIMED {format_number(pot)} {emoji}!**\n```\n{draw_board(board)}\n```")
    finally:
        active_players.discard(p1.id)
        active_players.discard(p2.id)

# ==================== Game Commands (Player vs Smart NPC) ====================
@bot.command(name="vsnpc")
async def vsnpc(ctx, amount: str):
    p1 = ctx.author
    if p1.id in active_players: 
        return
    p1_bal = get_balance(p1.id)
    bet_amount = p1_bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if bet_amount <= 0 or p1_bal["wallet"] < bet_amount:
        await ctx.send("❌ Insufficient coins!")
        return

    active_players.add(p1.id)
    p1_bal["wallet"] -= bet_amount
    save_data()
    pot = bet_amount * 2
    match_num = 1

    try:
        while True:
            board, tie, win_sym = ["⬜"] * 9, False, None
            board_msg = await ctx.send(f"🤖 **Match vs Smart NPC #{match_num}**\nYour turn (❌):\n```\n{draw_board(board)}\n```")
            while True:
                try:
                    m = await bot.wait_for('message', check=lambda m: m.author.id == p1.id and m.channel.id == ctx.channel.id and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(m.content) - 1
                    try: await m.delete()
                    except: pass
                except asyncio.TimeoutError:
                    win_sym = "⭕"
                    break
                
                if board[move] != "⬜": 
                    continue
                board[move] = "❌"
                
                res = check_winner(board)
                if res:
                    if res == "Tie": 
                        tie = True
                    else: 
                        win_sym = res
                    break

                # 🤖 វេនរបស់ AI Smart NPC
                await board_msg.edit(content="🤖 NPC is calculating smart move...\n```\n" + draw_board(board) + "\n```")
                await asyncio.sleep(1.0)
                
                npc_move = get_npc_move(board)
                board[npc_move] = "⭕"
                
                res = check_winner(board)
                if res:
                    if res == "Tie": 
                        tie = True
                    else: 
                        win_sym = res
                    break
                await board_msg.edit(content=f"🟢 Your turn (❌):\n```\n{draw_board(board)}\n```")
                
            if tie:
                await ctx.send("🤝 Tied with Smart NPC! Rematching...")
                match_num += 1
                continue
            break

        uid = str(p1.id)
        if win_sym == "❌":
            user_balances[uid]["wallet"] += pot
            user_balances[uid]["win"] += 1
            await ctx.send(f"🏆 {p1.mention} beat the Smart NPC and won {format_number(pot)} {emoji}!\n```\n{draw_board(board)}\n```")
        else:
            user_balances[uid]["lost"] += 1
            await ctx.send(f"💀 {p1.mention} lost to the Smart NPC! (-{format_number(bet_amount)} {emoji})\n```\n{draw_board(board)}\n```")
        save_data()
    finally:
        active_players.discard(p1.id)

# ==================== Bot Start Execution ====================
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token: 
        bot.run(token)
    else: 
        print("❌ Missing DISCORD_TOKEN in Environment Variables!")
