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

# Your custom emojis
emoji = "<:emoji_5:1516480628370047250>"
game_icon = "<:emoji_6:1516791105880985652>"

# Number formatter (e.g., 1000 -> 1,000)
def format_number(num):
    return "{:,}".format(num)

# Get or create player balance & statistics
def get_balance(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0}
    if "win" not in user_balances[user_id]:
        user_balances[user_id]["win"] = 0
        user_balances[user_id]["lost"] = 0
    return user_balances[user_id]

# Draw Tic-Tac-Toe Board
def draw_board(board):
    lines = []
    for i in range(0, 9, 3):
        lines.append(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    return "\n---------\n".join(lines)

# Check Winner System
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
    # ==================== Economy Commands (English) ====================
@bot.command(name="tbal")
async def tbal(ctx):
    bal = get_balance(ctx.author.id)
    wallet_fmt = format_number(bal['wallet'])
    bank_fmt = format_number(bal['bank'])
    lost_fmt = format_number(bal['lost'])
    win_fmt = format_number(bal['win'])
    
    embed = discord.Embed(
        title=f"💳 {ctx.author.display_name}'s Balance", 
        color=discord.Color.blue()
    )
    embed.description = (
        f"**Coins :** {wallet_fmt} {emoji}\n"
        f"**Bank :** {bank_fmt} {emoji}\n\n"
        f"📊 **Gameplay Statistics**\n"
        f"**Lost :** {lost_fmt} times\n"
        f"**Win :** {win_fmt} times"
    )
    embed.set_footer(text="Your personal coin profile")
    await ctx.send(embed=embed)

@bot.command(name="dep")
async def deposit(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["wallet"] < amt:
        await ctx.send("❌ Invalid amount or insufficient coins in your wallet!")
        return
    bal["wallet"] -= amt
    bal["bank"] += amt
    await ctx.send(f"✅ Successfully deposited {format_number(amt)} {emoji} into your bank!")

@bot.command(name="with")
async def withdraw(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["bank"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["bank"] < amt:
        await ctx.send("❌ Invalid amount or insufficient coins in your bank!")
        return
    bal["bank"] -= amt
    bal["wallet"] += amt
    await ctx.send(f"✅ Successfully withdrew {format_number(amt)} {emoji} to your wallet!")

# 🛠️ បន្ថែមបញ្ជាផ្ទេរលុយឱ្យគ្នា (tp @mention money) ជាភាសាអង់គ្លេស
@bot.command(name="tp")
async def transfer_money(ctx, receiver: discord.Member, amount: int):
    sender = ctx.author
    if sender == receiver or amount <= 0:
        await ctx.send("❌ Invalid action! You cannot transfer to yourself or enter a negative amount.")
        return
        
    sender_bal = get_balance(sender.id)
    receiver_bal = get_balance(receiver.id)
    
    if sender_bal["wallet"] < amount:
        await ctx.send(f"❌ {sender.display_name}, you do not have enough coins in your wallet to transfer {format_number(amount)} {emoji}!")
        return
        
    # ដំណើរការកាត់កងប្រាក់ផ្ទេរឱ្យគ្នា
    sender_bal["wallet"] -= amount
    receiver_bal["wallet"] += amount
    await ctx.send(f"✅ {sender.display_name} has successfully transferred {format_number(amount)} {emoji} to {receiver.display_name}!")

# Game Button View System (English Labels)
class AcceptDeclineView(discord.ui.View):
    def __init__(self, p2, timeout=60.0):
        super().__init__(timeout=timeout)
        self.p2 = p2
        self.value = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p2:
            await interaction.response.send_message("❌ This button is only for the player who was challenged!", ephemeral=True)
            return
        self.value = "accept"
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p2:
            await interaction.response.send_message("❌ This button is only for the player who was challenged!", ephemeral=True)
            return
        self.value = "decline"
        self.stop()
        # ==================== Game Commands (English) ====================
@bot.command(name="txo")
async def txo(ctx, p2: discord.Member, bet_amount: int):
    p1 = ctx.author
    if p1 == p2 or bet_amount <= 0:
        await ctx.send("❌ Cannot start the game! Invalid player or bet amount.")
        return
        
    if p1.id in active_players:
        await ctx.send(f"❌ {p1.display_name}, you are already in an active game!")
        return
    if p2.id in active_players:
        await ctx.send(f"❌ {p2.display_name} is currently playing another match!")
        return

    p1_bal, p2_bal = get_balance(p1.id), get_balance(p2.id)
    
    if p1_bal["wallet"] < bet_amount:
        await ctx.send(f"❌ {p1.display_name}, you do not have enough coins to bet {format_number(bet_amount)} {emoji}!")
        return
    if p2_bal["wallet"] < bet_amount:
        await ctx.send(f"❌ {p2.display_name} does not have enough coins to accept this bet of {format_number(bet_amount)} {emoji}!")
        return

    embed_invite = discord.Embed(
        title=f"{game_icon} Tic-Tac-Toe Challenge",
        color=discord.Color.blue()
    )
    embed_invite.description = (
        f"🎮 {p2.mention}! {p1.mention} has challenged you to a game of XO!\n"
        f"----------------------------------------\n"
        f"❌ Challenger (X) : {p1.display_name}\n"
        f"⭕ Opponent (O)   : {p2.display_name}\n"
        f"💵 Bet Amount      : {format_number(bet_amount)} {emoji}\n"
        f"----------------------------------------\n"
        f"👉 Click a button below to respond (60 seconds timeout):"
    )

    view = AcceptDeclineView(p2, timeout=60.0)
    msg = await ctx.send(embed=embed_invite, view=view)
    
    await view.wait()

    if view.value is None:
        for child in view.children: child.disabled = True
        await msg.edit(content="⏰ Invitation expired! No response received.", view=view)
        return

    if view.value == "decline":
        for child in view.children: child.disabled = True
        await msg.edit(content=f"❌ {p2.display_name} has declined the challenge!", view=view)
        return

    for child in view.children: child.disabled = True
    await msg.edit(content=f"✅ {p2.display_name} accepted the match! The game begins!", view=view)

    active_players.add(p1.id)
    active_players.add(p2.id)

    p1_bal["wallet"] -= bet_amount
    p2_bal["wallet"] -= bet_amount
    pot = bet_amount * 2
    match_num, turn, st_player = 1, p1, p1

    try:
        while True:
            embed_vs = discord.Embed(
                title="⚔️ Match 1vs1 Active ⚔️", 
                color=discord.Color.orange()
            )
            embed_vs.description = (
                f"**❌ {p1.display_name}**   Vs   **⭕ {p2.display_name}**\n"
                f"----------------------------------------\n"
                f"🏆 Match : #{match_num}\n"
                f"💵 Betting Amount : {format_number(bet_amount)} {emoji}\n"
                f"🎁 Winning Pool   : {format_number(pot)} {emoji}\n"
                f"----------------------------------------"
            )
            await ctx.send(embed=embed_vs)

            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"{turn.mention}'s turn ({'❌' if turn == p1 else '⭕'}):\n```{draw_board(board)}```\n⏰ *You have 5 minutes to play, don't AFK!*")
                try:
                    msg_turn = await bot.wait_for('message', check=lambda m: m.author == turn and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg_turn.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {turn.display_name} went AFK for over 5 minutes! Auto-defeat triggered!")
                    win_sym = '⭕' if turn == p1 else '❌'
                    break
                
                if board[move] != "⬜": 
                    await ctx.send("❌ This spot is already taken! Choose another number!")
                    continue
                    board[move] = '❌' if turn == p1 else '⭕'
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
                turn = p2 if turn == p1 else p1
                
            if tie:
                await ctx.send(f"🏁 It's a Tie!\n```{draw_board(board)}```\n🤝 Rematching instantly...")
                match_num += 1
                st_player = p2 if st_player == p1 else p1
                turn = st_player
                await asyncio.sleep(2)
                continue
            break

        winner = p1 if win_sym == '❌' else p2
        loser = p2 if winner == p1 else p1
        
        get_balance(winner.id)["wallet"] += pot
        get_balance(winner.id)["win"] += 1
        get_balance(loser.id)["lost"] += 1
        
        embed_end = discord.Embed(
            title="🏁 Match Concluded 🏁", 
            color=discord.Color.green()
        )
        embed_end.description = (
            f"👑 Winner : {winner.mention}\n"
            f"💀 Loser  : {loser.mention}\n"
            f"----------------------------------------\n"
            f"💵 Bet Amount   : {format_number(bet_amount)} {emoji}\n"
            f"🎁 Total Reward : {format_number(pot)} {emoji}\n"
            f"----------------------------------------"
        )
        await ctx.send(content=f"```{draw_board(board)}```", embed=embed_end)
        
    finally:
        active_players.discard(p1.id)
        active_players.discard(p2.id)

# ==================== VS NPC Command ====================
@bot.command(name="vsnpc")
async def vsnpc(ctx, amount: str):
    p1 = ctx.author
    if p1.id in active_players:
        await ctx.send(f"❌ {p1.display_name}, you are already in an active game!")
        return

    p1_bal = get_balance(p1.id)
    
    if amount.lower() == "all":
        bet_amount = p1_bal["wallet"]
    elif amount.isdigit():
        bet_amount = int(amount)
    else:
        await ctx.send("❌ Please provide a valid number or type all!")
        return

    if bet_amount <= 0:
        await ctx.send("❌ Bet amount must be greater than 0 coins!")
        return

    if p1_bal["wallet"] < bet_amount:
        await ctx.send(f"❌ {p1.display_name}, you do not have enough coins to bet {format_number(bet_amount)} {emoji}!")
        return

    active_players.add(p1.id)
    pot = bet_amount * 2

    embed_npc = discord.Embed(
        title="⚔️ Match Active (vs NPC) ⚔️", 
        color=discord.Color.purple()
    )
    embed_npc.description = (
        f"**❌ {p1.display_name}**   Vs   **🤖 NPC**\n"
        f"----------------------------------------\n"
        f"💵 Bet Amount   : {format_number(bet_amount)} {emoji}\n"
        f"🎁 Winning Pool : {format_number(pot)} {emoji}\n"
        f"----------------------------------------"
    )
    await ctx.send(embed=embed_npc)

    p1_bal["wallet"] -= bet_amount
    match_num = 1

    try:
        while True:
            await ctx.send(f"⚔️ Match vs NPC #{match_num}! (Pool: {format_number(pot)} {emoji})")
            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"🟢 Your turn ({p1.display_name} - ❌):\n```{draw_board(board)}```\n⏰ *You have 5 minutes to play!*")
                try:
                    msg = await bot.wait_for('message', check=lambda m: m.author == p1 and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {p1.display_name} went AFK! Game ended. NPC wins.")
                    win_sym = "⭕"
                    break
                
                if board[move] != "⬜": 
                    await ctx.send("❌ This spot is already taken! Choose another number!")
                    continue
                    
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
                await ctx.send(f"🏁 Tied match with NPC!\n```{draw_board(board)}```\n🤝 Rematching instantly...")
                match_num += 1
                await asyncio.sleep(2)
                continue
            break

        await ctx.send(f"🏁 Final Results:\n```{draw_board(board)}```")
        if win_sym == "❌":
            p1_bal["wallet"] += pot
            p1_bal["win"] += 1
            await ctx.send(f"🎉 {p1.mention} defeated NPC and won {format_number(pot)} {emoji}!")
        else:
            p1_bal["lost"] += 1
            await ctx.send(f"💸 {p1.mention} lost to NPC and dropped {format_number(bet_amount)} {emoji}!")
    finally:
        active_players.discard(p1.id)

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token: 
        bot.run(token)
    else:
        print("❌ DISCORD_TOKEN not found in Environment Variables!")
