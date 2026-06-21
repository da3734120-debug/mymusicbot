import discord
from discord.ext import commands, tasks
import asyncio
import os
import random
import json
from flask import Flask
from threading import Thread

# ==================== Web Server (Keep Bot Online) ====================
app = Flask('')

@app.route('/')
def home(): 
    return "Bot XO Online 24/7!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): 
    Thread(target=run_web_server).start()

# ==================== Database Setup (Volume) ====================
DATA_FILE = "database/balances.json"

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

# ==================== Bot Core Utilities ====================
intents = discord.Intents.default()
intents.message_content = True

# 🟢 កំណត់ឱ្យគ្មាន Prefix តាមបំណងរបស់បង (វាយពាក្យបញ្ជាចំៗបានភ្លាម)
bot = commands.Bot(command_prefix="", intents=intents, case_insensitive=True)

user_balances = load_data()
active_players = set()
def load_data_from_file():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def get_skin_style(user_id):
    bal = get_balance(user_id)
    active_skin = bal.get("active_skin", "Normal ✨")
    
    skin_colors = {
        "Wooden Shield 🪵": discord.Color.light_gray(),
        "Iron Sword ⚔️": discord.Color.blue(),
        "Shadow Cloak 🔮": discord.Color.purple(),
        "Dragon Relic 👑": discord.Color.orange(),
        "⚡ GODSLAYER AURA ⚡": discord.Color.from_rgb(139, 0, 0)
    }
    return skin_colors.get(active_skin, discord.Color.blue()), active_skin
@tasks.loop(minutes=5.0)
async def auto_save_backup():
    save_data()
    print("💾 [Auto-Save] Balances backed up to Volume successfully!")

# រូប Emoji ពិតប្រាកដរបស់បង
emoji = "<:emoji_5:1516480628370047250>" 
game_icon = "🎮"

def format_number(num):
    return "{:,}".format(num)

def get_balance(user_id):
    global user_balances
    uid = str(user_id)
    
    # 🔒 ថែមផ្នែកនេះ៖ បង្ខំឱ្យ main.py បើកអានឯកសារ JSON ចុងក្រោយបង្អស់ពី Volume ឡើងវិញជានិច្ច ដើម្បីទាញយកទិន្នន័យដែល Shop បានកាត់លុយរួច
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                user_balances = json.load(f)
        except Exception as e:
            print(f"⚠️ [get_balance] Failed to reload JSON File: {e}")

    # ប្រសិនបើមិនទាន់មានគណនីរបស់អ្នកលេងនេះទេ គឺបង្កើតគណនីថ្មីជូនភ្លាម
    if uid not in user_balances:
        user_balances[uid] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0, "inventory": []}
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
    if b[0] == b[4] == b[8] != "⬜": return b[4]
    if b[2] == b[4] == b[6] != "⬜": return b[4]
    if "⬜" not in b: return "Tie"
    return None

# 🧠 ប្រព័ន្ធខួរក្បាល AI NPC ឆ្លាតវៃ (ស្ទាក់បិទផ្លូវ និងវាយលុកយកជ័យជម្នះ)
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

    # ៣. យុទ្ធសាស្ត្រល្អ៖ វាយយកប្រអប់កណ្តាល (លេខ ៥ ឬ Index 4)
    if 4 in empty_spots:
        return 4

    # ៤. វាយលុកយកប្រអប់ជ្រុង (លេខ ១, ៣, ៧, ៩ ឬ Index 0, 2, 6, 8)
    corners = [0, 2, 6, 8]
    available_corners = [i for i in corners if i in empty_spots]
    if available_corners:
        return random.choice(available_corners)

    # ៥. ចុចជ្រើសរើសកន្លែងធម្មតាដែលនៅសល់
    return random.choice(empty_spots)
@bot.event
async def on_ready(): 
    print(f'📢 Bot XO Online: {bot.user.name}')
    
    # 🔌 ហៅប្រព័ន្ធ T/help
    try:
        await bot.load_extension("help_command")
        print("✅ Loaded help_command.py successfully!")
    except Exception as e:
        print(f"❌ Failed to load help_command: {e}")

    # 🔌 ហៅប្រព័ន្ធ T/shop ថ្មី (ត្រូវប្រាកដថាឈ្មោះដូចគ្នាបេះបិទ)
    try:
        await bot.load_extension("shop_command")
        print("✅ Loaded shop_command.py successfully!")
    except Exception as e:
        print(f"❌ Failed to load shop_command: {e}")
        
    auto_save_backup.start()
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
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text="Your personal coin profile")
    await ctx.send(embed=embed)

@bot.command(name="Tbank")
async def deposit(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["wallet"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    
    if amt <= 0 or bal["wallet"] < amt:
        embed_error = discord.Embed(title="❌ Transaction Failed", description="Invalid amount or insufficient coins in your wallet!", color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return
    
    bal["wallet"] -= amt
    bal["bank"] += amt
    save_data()
    
    embed_success = discord.Embed(title="🏦 Deposit Successful", color=discord.Color.green())
    embed_success.description = (
        f"👤 Account: {ctx.author.mention}\n"
        f"📥 Deposited: +{format_number(amt)} {emoji} into Bank\n"
        f"--------------------------------\n"
        f"💰 Current Wallet: {format_number(bal['wallet'])} {emoji}"
    )
    if ctx.author.avatar:
        embed_success.set_thumbnail(url=ctx.author.avatar.url)
    embed_success.set_footer(text="XO Online Bank System")
    await ctx.send(embed=embed_success)

@bot.command(name="Tout")
async def withdraw(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["bank"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    
    if amt <= 0 or bal["bank"] < amt:
        embed_error = discord.Embed(title="❌ Transaction Failed", description="Invalid amount or insufficient coins in your bank!", color=discord.Color.red())
        await ctx.send(embed=embed_error)
        return
    
    bal["bank"] -= amt
    bal["wallet"] += amt
    save_data()
    
    embed_success = discord.Embed(title="💸 Withdraw Successful", color=discord.Color.blue())
    embed_success.description = (
        f"👤 Account: {ctx.author.mention}\n"
        f"📤 Withdrew: +{format_number(amt)} {emoji} to Wallet\n"
        f"--------------------------------\n"
        f"💰 Current Bank: {format_number(bal['bank'])} {emoji}"
    )
    if ctx.author.avatar:
        embed_success.set_thumbnail(url=ctx.author.avatar.url)
    embed_success.set_footer(text="XO Online Bank System")
    await ctx.send(embed=embed_success)

@bot.command(name="tp")
async def transfer_money(ctx, receiver: discord.Member, amount: int):
    sender = ctx.author
    if sender.id == receiver.id or amount <= 0:
        await ctx.send("❌ Invalid action! You cannot transfer to yourself.")
        return
    sender_bal = get_balance(sender.id)
    receiver_bal = get_balance(receiver.id)
    if sender_bal["wallet"] < amount:
        await ctx.send(f"❌ {sender.display_name}, you do not have enough coins!")
        return

    embed_tp = discord.Embed(title="💸 Money Transfer Pending", color=discord.Color.gold())
    embed_tp.description = (
        f"👤 Sender: {sender.mention}\n"
        f"🎯 Receiver: {receiver.mention}\n"
        f"💵 Amount: {format_number(amount)} {emoji}\n\n"
        f"👉 {sender.mention}, are you sure you want to transfer? Click a button below:\n(Timeout: 60s)"
    )
    if sender.avatar:
        embed_tp.set_thumbnail(url=sender.avatar.url)

    view = QuickButtonView(allowed_user=sender, timeout=60.0)
    msg = await ctx.send(content=f"{sender.mention} Please confirm your transfer!", embed=embed_tp, view=view)
    await view.wait()

    if view.value is None or view.value == "decline":
        for child in view.children: child.disabled = True
        embed_tp.title = "❌ Transfer Cancelled / Expired"
        embed_tp.color = discord.Color.red()
        embed_tp.description = "❌ The transaction was declined or timed out."
        await msg.edit(content=None, embed=embed_tp, view=view)
        return

    for child in view.children: child.disabled = True
    sender_bal["wallet"] -= amount
    receiver_bal["wallet"] += amount
    save_data()

    embed_success = discord.Embed(title="✅ Transfer Completed", color=discord.Color.green())
    embed_success.description = (
        f"🎉 Transaction finished successfully!\n"
        f"----------------------------------------\n"
        f"📉 Sender: {sender.mention} (-{format_number(amount)} {emoji})\n"
        f"📈 Receiver: {receiver.mention} (+{format_number(amount)} {emoji})\n"
        f"----------------------------------------\n"
        f"💰 Sender's Remaining Wallet: {format_number(sender_bal['wallet'])} {emoji}"
    )
    await msg.edit(content=None, embed=embed_success, view=view)
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

    view = QuickButtonView(allowed_user=p2, timeout=60.0)
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
    save_data()
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
            vs_msg = await ctx.send(embed=embed_vs)

            board, tie, win_sym = ["⬜"] * 9, False, None
            board_msg = await ctx.send(f"{turn.mention}'s turn ({'❌' if turn == p1 else '⭕'}):\n```{draw_board(board)}```\n⏰ *5 minutes timeout!*")
            
            while True:
                try:
                    msg_turn = await bot.wait_for('message', check=lambda m: m.author.id == turn.id and m.channel.id == ctx.channel.id and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg_turn.content) - 1
                    try: await msg_turn.delete()
                    except: pass
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {turn.display_name} went AFK! Auto-defeat triggered!")
                    win_sym = '⭕' if turn == p1 else '❌'
                    break
                    
                if board[move] != "⬜": 
                    warning = await ctx.send("❌ This spot is already taken! Try again.")
                    await asyncio.sleep(2)
                    try: await warning.delete()
                    except: pass
                    continue

                board[move] = '❌' if turn == p1 else '⭕'
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
                turn = p2 if turn == p1 else p1
                await board_msg.edit(content=f"{turn.mention}'s turn ({'❌' if turn == p1 else '⭕'}):\n```{draw_board(board)}```\n⏰ *5 minutes timeout!*")
                
            try: await board_msg.delete()
            except: pass
            try: await vs_msg.delete()
            except: pass

            if tie:
                await ctx.send(f"🏁 It's a Tie!\n```{draw_board(board)}```\n🤝 Rematching to next round...")
                match_num += 1
                st_player = p2 if st_player == p1 else p1
                turn = st_player
                await asyncio.sleep(2)
                continue
            break

        winner = p1 if win_sym == '❌' else p2
        loser = p2 if winner == p1 else p1
        user_balances[str(winner.id)]["wallet"] += pot
        user_balances[str(winner.id)]["win"] += 1
        user_balances[str(loser.id)]["lost"] += 1
        save_data()
        
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
    await ctx.send(embed=embed_npc)
    p1_bal["wallet"] -= bet_amount
    save_data()

    try:
        while True:
            await ctx.send(f"⚔️ Match vs NPC #{match_num}!")
            board, tie, win_sym = ["⬜"] * 9, False, None
            board_msg = await ctx.send(f"🟢 Your turn (❌):\n```{draw_board(board)}```")
            
            while True:
                try:
                    msg = await bot.wait_for('message', check=lambda m: m.author.id == p1.id and m.channel.id == ctx.channel.id and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg.content) - 1
                    try: await msg.delete()
                    except: pass
                except asyncio.TimeoutError:
                    await ctx.send("⏰ You went AFK! NPC wins.")
                    win_sym = "⭕"
                    break
                
                if board[move] != "⬜": 
                    warning = await ctx.send("❌ This spot is already taken! Try again.")
                    await asyncio.sleep(2)
                    try: await warning.delete()
                    except: pass
                    continue
                    
                board[move] = "❌"
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break

                # 🤖 វេនរបស់ AI Smart NPC ឆ្លាតវៃ
                await board_msg.edit(content="🤖 NPC is thinking...\n```" + draw_board(board) + "```")
                await asyncio.sleep(1.0)
                
                npc_move = get_npc_move(board)
                board[npc_move] = "⭕"
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
                await board_msg.edit(content=f"🟢 Your turn (❌):\n```{draw_board(board)}```")
            
            try: await board_msg.delete()
            except: pass

            if tie:
                await ctx.send(f"🏁 Tied with NPC!\n```{draw_board(board)}```\n🤝 Rematching...")
                match_num += 1
                await asyncio.sleep(2)
                continue
            break

        await ctx.send(f"🏁 Final Results:\n```{draw_board(board)}```")
        uid = str(p1.id)
        if win_sym == "❌":
            user_balances[uid]["wallet"] += pot
            user_balances[uid]["win"] += 1
            await ctx.send(f"🎉 {p1.mention} defeated NPC and won {format_number(pot)} {emoji}!")
        else:
            user_balances[uid]["lost"] += 1
            await ctx.send(f"💸 {p1.mention} lost to NPC and dropped {format_number(bet_amount)} {emoji}!")
        
        save_data()
    finally:
        active_players.discard(p1.id)

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
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token: 
        bot.run(token)
    else:
        print("❌ DISCORD_TOKEN not found in Environment Variables!")
