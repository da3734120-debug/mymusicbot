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

# រូបកាក់របស់បង
emoji = "<:emoji_5:1516480628370047250>"

# 🛠️ បន្ថែមរូបសញ្ញាថ្មីជំនួសដៃហ្គេម 🎮 តាមដែលបងបានផ្ញើមក
game_icon = "<:emoji_6:1516791105880985652>"

# មុខងារបំប្លែងលេខឱ្យមានសញ្ញាក្បៀស (ឧទាហរណ៍៖ 1000 -> 1,000)
def format_number(num):
    return "{:,}".format(num)

# បង្កើត ឬទាញយកទិន្នន័យគណនី និងស្ថិតិឈ្នះ/ចាញ់
def get_balance(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0}
    if "win" not in user_balances[user_id]:
        user_balances[user_id]["win"] = 0
        user_balances[user_id]["lost"] = 0
    return user_balances[user_id]

# គូរផ្ទាំងក្តារ XO
def draw_board(board):
    lines = []
    for i in range(0, 9, 3):
        lines.append(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    return "\n---------\n".join(lines)

# ប្រព័ន្ធឆែករកអ្នកឈ្នះ
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
    # ==================== Command មើលលុយ (tbal) ====================
@bot.command(name="tbal")
async def tbal(ctx):
    bal = get_balance(ctx.author.id)
    wallet_fmt = format_number(bal['wallet'])
    bank_fmt = format_number(bal['bank'])
    lost_fmt = format_number(bal['lost'])
    win_fmt = format_number(bal['win'])
    
    embed = discord.Embed(
        title=f"💳 គណនីរបស់ {ctx.author.name}", 
        color=discord.Color.blue()
    )
    embed.description = (
        f"**Coins :** {wallet_fmt} {emoji}\n"
        f"**Bank :** {bank_fmt} {emoji}\n\n"
        f"📊 **ស្ថិតិការលេង (Gameplay)**\n"
        f"**Lost :** {lost_fmt} ដង\n"
        f"**Win :** {win_fmt} ដង"
    )
    
    embed.set_footer(text="សញ្ញាសម្គាល់កាក់ប្រចាំខ្លួនបង")
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
    await ctx.send(f"✅ បានដាក់លុយ {format_number(amt)} {emoji} ចូលធនាគាររួចរាល់!")

@bot.command(name="with")
async def withdraw(ctx, amount: str):
    bal = get_balance(ctx.author.id)
    amt = bal["bank"] if amount.lower() == "all" else (int(amount) if amount.isdigit() else 0)
    if amt <= 0 or bal["bank"] < amt:
        await ctx.send("❌ លុយមិនត្រឹមត្រូវ ឬមិនគ្រប់គ្រាន់ទេ!")
        return
    bal["bank"] -= amt
    bal["wallet"] += amt
    await ctx.send(f"✅ បានដកលុយ {format_number(amt)} {emoji} មកកាបូបរួចរាល់!")

# 🛠️ បង្កើតប្រព័ន្ធប៊ូតូនចុច Accept (បៃតងខាងឆ្វេង) និង Decline (ក្រហមខាងស្តាំ)
class AcceptDeclineView(discord.ui.View):
    def __init__(self, p2, timeout=60.0):
        super().__init__(timeout=timeout)
        self.p2 = p2
        self.value = None

    # ប៊ូតូនបៃតងខាងឆ្វេង (Accept)
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p2:
            await interaction.response.send_message("❌ ប៊ូតូននេះសម្រាប់តែអ្នកដែលត្រូវបានបបួលប៉ុណ្ណោះ!", ephemeral=True)
            return
        self.value = "accept"
        self.stop()

    # ប៊ូតូនក្រហមខាងស្តាំ (Decline)
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p2:
            await interaction.response.send_message("❌ ប៊ូតូននេះសម្រាប់តែអ្នកដែលត្រូវបានបបួលប៉ុណ្ណោះ!", ephemeral=True)
            return
        self.value = "decline"
        self.stop()
        # ==================== Command ពេលប្រកួត (txo) ====================
@bot.command(name="txo")
async def txo(ctx, p2: discord.Member, bet_amount: int):
    p1 = ctx.author
    if p1 == p2 or bet_amount <= 0:
        await ctx.send("❌ មិនអាចលេងបានទេ!")
        return
        
    if p1.id in active_players:
        await ctx.send(f"❌ {p1.mention} អ្នកកំពុងជាប់លេងហ្គេមមួយរួចហើយ!")
        return
    if p2.id in active_players:
        await ctx.send(f"❌ {p2.mention} កំពុងជាប់លេងហ្គេមជាមួយអ្នកផ្សេងរួចហើយ!")
        return

    p1_bal, p2_bal = get_balance(p1.id), get_balance(p2.id)
    if p1_bal["wallet"] < bet_amount or p2_bal["wallet"] < bet_amount:
        await ctx.send("❌ មានភាគីម្ខាងខ្វះលុយក្នុងកាបូប!")
        return

    # 🛠️ កែសម្រួល៖ ប្រើប្រាស់រូបសញ្ញាថ្មី game_icon របស់បង និងណែនាំឱ្យចុចប៊ូតូន
    view = AcceptDeclineView(p2, timeout=60.0)
    msg = await ctx.send(
        f"{game_icon} {p2.mention}! {p1.mention} បបួលលេង XO ភ្នាល់ចំនួន {format_number(bet_amount)} {emoji}!\n"
        f"📌 **{p1.name}**=❌ | **{p2.name}**=⭕\n"
        f"👉 សូមចុចប៊ូតូនខាងក្រោមដើម្បីឆ្លើយតប (មានពេល ៦០ វិនាទី)៖", 
        view=view
    )
    
    # រង់ចាំអ្នកលេងចុចប៊ូតូន
    await view.wait()

    # ករណីហួសពេលកំណត់ (Timeout)
    if view.value is None:
        # បិទប៊ូតូនកុំឱ្យចុចកើតទៀត
        for child in view.children:
            child.disabled = True
        await msg.edit(content=f"⏰ ហួសពេលកំណត់ក្នុងការទទួលការបបួល! (បិទការចុច)", view=view)
        return

    # ករណីចុចបដិសេធ (Decline)
    if view.value == "decline":
        for child in view.children:
            child.disabled = True
        await msg.edit(content=f"❌ {p2.mention} បានបដិសេធការបបួលលេង!", view=view)
        return

    # ករណីចុចព្រមលេង (Accept) - ចាប់ផ្តើមហ្គេម
    for child in view.children:
        child.disabled = True
    await msg.edit(content=f"✅ {p2.mention} បានយល់ព្រមចូលរួមលេង! ហ្គេមចាប់ផ្តើម!", view=view)

    active_players.add(p1.id)
    active_players.add(p2.id)

    p1_bal["wallet"] -= bet_amount
    p2_bal["wallet"] -= bet_amount
    pot = bet_amount * 2
    match_num, turn, st_player = 1, p1, p1

    try:
        while True:
            embed_vs = discord.Embed(
                title="⚔️ ការប្រកួត 1vs1 ⚔️", 
                color=discord.Color.orange()
            )
            embed_vs.description = (
                f"**❌ {p1.name}**   Vs   **⭕ {p2.name}**\n"
                f"----------------------------------------\n"
                f"🏆 ប្រកួតទី : {match_num}\n"
                f"💵 លុយដែលភ្នាល់ : {format_number(bet_amount)} {emoji}\n"
                f"🎁 លុយដែលឈ្នះ : {format_number(pot)} {emoji}\n"
                f"----------------------------------------"
            )
            await ctx.send(embed=embed_vs)

            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"វេនរបស់ {turn.mention} ({'❌' if turn == p1 else '⭕'}):\n```{draw_board(board)}```\n⏰ *មានពេល ៥ នាទីក្នុងការចុចដើរ!*")
                try:
                    msg_turn = await bot.wait_for('message', check=lambda m: m.author == turn and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg_turn.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {turn.mention} បាន AFK លើសពី ៥ នាទី! ត្រូវបានកាត់សេចក្តីឱ្យចាញ់ភ្លាមៗ!")
                    win_sym = '⭕' if turn == p1 else '❌'
                    break
                
                if board[move] != "⬜": 
                    await ctx.send("❌ ប្រអប់នេះមានគេដៅរួចហើយ! សូមជ្រើសរើសលេខផ្សេង!")
                    continue
                    
                board[move] = '❌' if turn == p1 else '⭕'
                res = check_winner(board)
                if res:
                    if res == "Tie": tie = True
                    else: win_sym = res
                    break
                turn = p2 if turn == p1 else p1
                
            if tie:
                await ctx.send(f"🏁 ស្មើគ្នា!\n```{draw_board(board)}```\n🤝 ប្រកួតឡើងវិញភ្លាមៗ...")
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
            title="🏁 បញ្ចប់ការប្រកួត 🏁", 
            color=discord.Color.green()
        )
        embed_end.description = (
            f"👑 អ្នកឈ្នះ : {winner.mention}\n"
            f"💀 អ្នកចាញ់ : {loser.mention}\n"
            f"----------------------------------------\n"
            f"💵 លុយភ្នាល់ : {format_number(bet_amount)} {emoji}\n"
            f"🎁 ប្រាក់រង្វាន់ដែលទទួលបាន : {format_number(pot)} {emoji}\n"
            f"----------------------------------------"
        )
        await ctx.send(content=f"```{draw_board(board)}```", embed=embed_end)
        
    finally:
        active_players.discard(p1.id)
        active_players.discard(p2.id)

# ==================== ផ្នែកលេងជាមួយ NPC (vsnpc) ====================
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
    pot = bet_amount * 2

    embed_npc = discord.Embed(
        title="⚔️ ការប្រកួត 1vs1 (ទល់នឹង NPC) ⚔️", 
        color=discord.Color.purple()
    )
    embed_npc.description = (
        f"**❌ {p1.name}**   Vs   **🤖 NPC**\n"
        f"----------------------------------------\n"
        f"💵 លុយដែលភ្នាល់ : {format_number(bet_amount)} {emoji}\n"
        f"🎁 លុយដែលឈ្នះ : {format_number(pot)} {emoji}\n"
        f"----------------------------------------"
    )
    await ctx.send(embed=embed_npc)

    p1_bal["wallet"] -= bet_amount
    match_num = 1

    try:
        while True:
            await ctx.send(f"⚔️ ប្រកួតទល់នឹង NPC ទី {match_num}! (ក្នុងក្អម៖ {format_number(pot)} {emoji})")
            board, tie, win_sym = ["⬜"] * 9, False, None
            while True:
                await ctx.send(f"🟢 វេនរបស់ {p1.mention} (❌):\n```{draw_board(board)}```\n⏰ *មានពេល ៥ នាទីក្នុងការចុចដើរ!*")
                try:
                    msg = await bot.wait_for('message', check=lambda m: m.author == p1 and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 9, timeout=300.0)
                    move = int(msg.content) - 1
                except asyncio.TimeoutError:
                    await ctx.send(f"⏰ {p1.mention} ទុកចោលលើសពី ៥ នាទី! ហ្គេមត្រូវបានបញ្ចប់ ហើយ NPC ជាអ្នកឈ្នះ។")
                    win_sym = "⭕"
                    break
                
                if board[move] != "⬜": 
                    await ctx.send("❌ ប្រអប់នេះមានគេដៅរួចហើយ! សូមជ្រើសរើសលេខផ្សេង!")
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
                await ctx.send(f"🏁 ស្មើគ្នាជាមួយ NPC!\n```{draw_board(board)}```\n🤝 លេងឡើងវិញភ្លាមៗ...")
                match_num += 1
                await asyncio.sleep(2)
                continue
            break

        await ctx.send(f"🏁 លទ្ធផលចុងក្រោយ:\n```{draw_board(board)}```")
        if win_sym == "❌":
            p1_bal["wallet"] += pot
            p1_bal["win"] += 1
            await ctx.send(f"🎉 {p1.mention} ឈ្នះ NPC បាន {format_number(pot)} {emoji}!")
        else:
            p1_bal["lost"] += 1
            await ctx.send(f"💸 {p1.mention} ចាញ់ NPC អស់ {format_number(bet_amount)} {emoji}!")
    finally:
        active_players.discard(p1.id)

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token: 
        bot.run(token)
    else:
        print("❌ រកមិនឃើញ DISCORD_TOKEN នៅក្នុង Environment Variable ទេ!")
