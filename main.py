import discord
from discord.ext import commands
import asyncio
import os
import random
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): 
    return "Bot XO Online 24/7!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): 
    Thread(target=run_web_server).start()

intents = discord.Intents.default()
intents.message_content = True
# កំណត់ Prefix ទៅជាទទេរ (វាយពាក្យសុទ្ធ គ្មានសញ្ញា !)
bot = commands.Bot(command_prefix="", intents=intents, case_insensitive=True)

user_balances = {}
active_players = set()

# រូប Emoji លុយពិតប្រាកដរបស់បង
emoji = "<:emoji_5:1516480628370047250>" 
game_icon = "🎮"

def format_number(num):
    return "{:,}".format(num)

def get_balance(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0}
    if "win" not in user_balances[user_id]:
        user_balances[user_id]["win"] = 0
        user_balances[user_id]["lost"] = 0
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
    if b == b == b != "⬜": return b
    if b == b == b != "⬜": return b
    if "⬜" not in b: return "Tie"
    return None

@bot.event
async def on_ready(): 
    print(f'📢 Bot XO Online: {bot.user.name}')

# ==================== Economy Commands ====================
@bot.command(name="tbal")
async def tbal(ctx):
    bal = get_balance(ctx.author.id)
    wallet_fmt = format_number(bal['wallet'])
    bank_fmt = format_number(bal['bank'])
    lost_fmt = format_number(bal['lost'])
    win_fmt = format_number(bal['win'])
    
    embed = discord.Embed(title=f"💳 {ctx.author.display_name}'s Balance", color=discord.Color.blue())
    embed.description = (
        f"**Coins :** {wallet_fmt} {emoji}\n"
        f"**Bank :** {bank_fmt} {emoji}\n\n"
        f"📊 **Gameplay Statistics**\n"
        f"**Lost :** {lost_fmt} times\n"
        f"**Win :** {win_fmt} times"
    )
    embed.set_footer(text="Your personal coin profile")
    await ctx.send(embed=embed)

@bot.command(name="Tbank")
async def deposit(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["wallet"] < amt:
        await ctx.send("❌ Invalid amount or insufficient coins in your wallet!")
        return
    bal["wallet"] -= amt
    bal["bank"] += amt
    await ctx.send(f"✅ Successfully deposited {format_number(amt)} {emoji} into your bank via Tbank!")

@bot.command(name="Tout")
async def withdraw(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["bank"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["bank"] < amt:
        await ctx.send("❌ Invalid amount or insufficient coins in your bank!")
        return
    bal["bank"] -= amt
    bal["wallet"] += amt
    await ctx.send(f"✅ Successfully withdrew {format_number(amt)} {emoji} to your wallet via Tout!")

# ប៊ូតុងប្រព័ន្ធផ្ទេរលុយ (សម្រាប់តែអ្នកផ្ញើ ឬម្ចាស់លុយចុចបញ្ជាក់ប៉ុណ្ណោះ)
class TransferSenderView(discord.ui.View):
    def __init__(self, sender, timeout=60.0):
        super().__init__(timeout=timeout)
        self.sender = sender
        self.value = None

    @discord.ui.button(label="Accept (ប្រាកដណាស់) ✅", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.sender:
            await interaction.response.send_message("❌ ប៊ូតុងនេះសម្រាប់តែម្ចាស់លុយ (អ្នកផ្ញើ) ចុចបញ្ជាក់ប៉ុណ្ណោះ!", ephemeral=True)
            return
        self.value = "accept"
        self.stop()

    @discord.ui.button(label="Decline (បដិសេធ) ❌", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.sender:
            await interaction.response.send_message("❌ ប៊ូតុងនេះសម្រាប់តែម្ចាស់លុយ (អ្នកផ្ញើ) ចុចបដិសេធប៉ុណ្ណោះ!", ephemeral=True)
            return
        self.value = "decline"
        self.stop()

@bot.command(name="tp")
async def transfer_money(ctx, receiver: discord.Member, amount: int):
    sender = ctx.author
    if sender == receiver or amount <= 0:
        await ctx.send("❌ Action មិនត្រឹមត្រូវ! អ្នកមិនអាចផ្ទេរលុយឱ្យខ្លួនឯង ឬដាក់ចំនួនដកបានទេ។")
        return
    sender_bal = get_balance(sender.id)
    receiver_bal = get_balance(receiver.id)
    if sender_bal["wallet"] < amount:
        await ctx.send(f"❌ {sender.display_name}, អ្នកមិនមានលុយគ្រប់គ្រាន់ក្នុងកាបូបទេ!")
        return

    # បង្កើត Embed សួរទៅកាន់អ្នកផ្ញើ
    embed_tp = discord.Embed(title="💸 ការផ្ទេរប្រាក់ (Money Transfer Pending)", color=discord.Color.gold())
    embed_tp.description = (
        f"👤 អ្នកផ្ញើ (Sender): {sender.mention}\n"
        f"🎯 អ្នកទទួល (Receiver): {receiver.mention}\n"
        f"💵 ចំនួនទឹកប្រាក់: {format_number(amount)} {emoji}\n\n"
        f"👉 {sender.mention} តើអ្នកប្រាកដជាចង់ផ្ទេរលុយនេះទៅឱ្យគេមែនទេ? សូមចុចប៊ូតុងខាងក្រោម៖\n(Timeout: 60s)"
    )
    if sender.avatar:
        embed_tp.set_thumbnail(url=sender.avatar.url)

    view = TransferSenderView(sender, timeout=60.0)
    msg = await ctx.send(content=f"{sender.mention} សូមបញ្ជាក់ការផ្ទេរប្រាក់របស់អ្នក!", embed=embed_tp, view=view)
    await view.wait()

    if view.value is None:
        for child in view.children: child.disabled = True
        embed_tp.title = "⏰ ការផ្ទេរប្រាក់ (អស់ពេល)"
        embed_tp.color = discord.Color.greyple()
        embed_tp.description = f"❌ ការផ្ទេរប្រាក់ត្រូវបានលុបចោល ដោយសារគ្មានការឆ្លើយតបឆ្លងកាត់រយៈពេល ៦០ វិនាទី។"
        await msg.edit(content=None, embed=embed_tp, view=view)
        return

    if view.value == "decline":
        for child in view.children: child.disabled = True
        embed_tp.title = "❌ ការផ្ទេរប្រាក់ (ត្រូវបានបដិសេធ)"
        embed_tp.color = discord.Color.red()
        embed_tp.description = f"❌ {sender.mention} បានផ្លាស់ប្តូរចិត្ត និងចុចបដិសេធការផ្ទេរប្រាក់នេះ!"
        await msg.edit(content=None, embed=embed_tp, view=view)
        return

    # នៅពេលអ្នកផ្ញើចុច Accept ទើបប្រព័ន្ធកាត់លុយផ្ទេរជាផ្លូវការ
    for child in view.children: child.disabled = True
    sender_bal["wallet"] -= amount
    receiver_bal["wallet"] += amount

    embed_success = discord.Embed(title="✅ ផ្ទេរប្រាក់ជោគជ័យ! (Transfer Completed)", color=discord.Color.green())
    embed_success.description = (
        f"🎉 ការផ្ទេរប្រាក់ត្រូវបានបញ្ចប់ដោយជោគជ័យ!\n"
        f"----------------------------------------\n"
        f"📉 Sender: {sender.mention} (-{format_number(amount)} {emoji})\n"
        f"📈 Receiver: {receiver.mention} (+{format_number(amount)} {emoji})\n"
        f"----------------------------------------\n"
        f"💰 សមតុល្យក្នុងកាបូបរបស់អ្នកផ្ញើ៖ {format_number(sender_bal['wallet'])} {emoji}"
    )
    await msg.edit(content=None, embed=embed_success, view=view)

# ប៊ូតុងយល់ព្រមលេងហ្គេម XO
class AcceptDeclineView(discord.ui.View):
    def __init__(self, p2, timeout=60.0):
        super().__init__(timeout=timeout)
        self.p2 = p2
        self.value = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p2:
            await interaction.response.send_message("❌ ប៊ូតុងនេះសម្រាប់តែអ្នកដែលគេបបួលលេងប៉ុណ្ណោះ!", ephemeral=True)
            return
        self.value = "accept"
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p2:
            await interaction.response.send_message("❌ ប៊ូតុងនេះសម្រាប់តែអ្នកដែលគេបបួលលេងប៉ុណ្ណោះ!", ephemeral=True)
            return
        self.value = "decline"
        self.stop()
        # ==================== Game Commands (Player vs Player) ====================
@bot.command(name="txo")
async def txo(ctx, p2: discord.Member, bet_amount: int):
    p1 = ctx.author
    if p1 == p2 or bet_amount <= 0:
        await ctx.send("❌ Cannot start the game! Invalid player or bet amount.")
        return
    if p1.id in active_players or p2.id in active_players:
        await ctx.send("❌ One of the players is already in an active game!")
        return

    p1_bal, p2_bal = get_balance(p1.id), get_balance(p2.id)
    if p1_bal["wallet"] < bet_amount or p2_bal["wallet"] < bet_amount:
        await ctx.send("❌ Insufficient coins to start the match!")
        return

    embed_invite = discord.Embed(title=f"{game_icon} Tic-Tac-Toe Challenge", color=discord.Color.blue())
    embed_invite.description = (
        f"🎮 {p2.mention}! {p1.mention} has challenged you to a game of XO!\n"
        f"----------------------------------------\n"
        f"❌ Challenger (X) : {p1.display_name}\n"
        f"⭕ Opponent (O)   : {p2.display_name}\n"
        f"💵 Bet Amount      : {format_number(bet_amount)} {emoji}\n"
        f"----------------------------------------\n"
        f"👉 Click a button below to respond:"
    )

    view = AcceptDeclineView(p2, timeout=60.0)
    msg = await ctx.send(embed=embed_invite, view=view)
    await view.wait()

    if view.value is None or view.value == "decline":
        for child in view.children: child.disabled = True
        status_text = "⏰ Invitation expired!" if view.value is None else f"❌ {p2.display_name} declined!"
        await msg.edit(content=status_text, view=view)
        return

    for child in view.children: child.disabled = True
    await msg.edit(content=f"✅ {p2.display_name} accepted the match!", view=view)

    active_players.add(p1.id)
    active_players.add(p2.id)
    p1_bal["wallet"] -= bet_amount
    p2_bal["wallet"] -= bet_amount
    pot = bet_amount * 2
    match_num, turn, st_player = 1, p1, p1

    try:
        while True:
            embed_vs = discord.Embed(title="⚔️ Match 1vs1 Active ⚔️", color=discord.Color.orange())
            embed_vs.description = (
                f"**❌ {p1.display_name}**   Vs   **⭕ {p2.display_name}**\n"
                f"----------------------------------------\n"
                f"🏆 Match : #{match_num}\n"
                f"🎁 Winning Pool   : {format_number(pot)} {emoji}\n"
                f"----------------------------------------"
            )
            await ctx.send(embed=embed_vs)

            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"{turn.mention}'s turn ({'❌' if turn == p1 else '⭕'}):\n```{draw_board(board)}```\n⏰ *5 minutes timeout!*")
                try:
                    msg_turn = await bot.wait_for('message', check=lambda m: m.author == turn and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg_turn.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {turn.display_name} went AFK! Auto-defeat triggered!")
                    win_sym = '⭕' if turn == p1 else '❌'
                    break
                
                if board[move] != "⬜": 
                    await ctx.send("❌ This spot is already taken!")
                    continue

                board[move] = '❌' if turn == p1 else '⭕'
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
                turn = p2 if turn == p1 else p1
                
            if tie:
                await ctx.send(f"🏁 It's a Tie!\n```{draw_board(board)}```\n🤝 Rematching...")
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
        
        embed_end = discord.Embed(title="🏁 Match Concluded 🏁", color=discord.Color.green())
        embed_end.description = (
            f"👑 Winner : {winner.mention}\n"
            f"💀 Loser  : {loser.mention}\n"
            f"🎁 Total Reward : {format_number(pot)} {emoji}"
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
        await ctx.send(f"❌ {p1.display_name}, you are already in a game!")
        return

    p1_bal = get_balance(p1.id)
    bet_amount = p1_bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)

    if bet_amount <= 0 or p1_bal["wallet"] < bet_amount:
        await ctx.send("❌ Invalid bet amount or insufficient coins!")
        return

    active_players.add(p1.id)
    pot = bet_amount * 2
    match_num = 1

    embed_npc = discord.Embed(title="⚔️ Match Active (vs NPC) ⚔️", color=discord.Color.purple())
    embed_npc.description = (
        f"**❌ {p1.display_name}**   Vs   **🤖 NPC**\n"
        f"----------------------------------------\n"
        f"🎁 Winning Pool : {format_number(pot)} {emoji}\n"
        f"----------------------------------------"
    )
    await ctx.send(embed=npc)
    p1_bal["wallet"] -= bet_amount

    try:
        while True:
            await ctx.send(f"⚔️ Match vs NPC #{match_num}!")
            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"🟢 Your turn (❌):\n```{draw_board(board)}```")
                try:
                    msg = await bot.wait_for('message', check=lambda m: m.author == p1 and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send("⏰ You went AFK! NPC wins.")
                    win_sym = "⭕"
                    break
                
                if board[move] != "⬜": 
                    await ctx.send("❌ This spot is already taken!")
                    continue
                    
                board[move] = "❌"
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break

                # NPC Turn
                await asyncio.sleep(1.0)
                empty = [i for i, c in enumerate(board) if c == "⬜"]
                if empty:
                    board[random.choice(empty)] = "⭕"
                    res = check_winner(board)
                    if res:
                        if res == "Tie": tie = True
                        else: win_sym = res
                        break
                    
            if tie:
                await ctx.send(f"🏁 Tied with NPC!\n```{draw_board(board)}```\n🤝 Rematching...")
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
