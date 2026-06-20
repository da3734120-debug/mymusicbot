import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="t/help")
    async def help_command(self, ctx):
        # 👑 Premium Gold-themed Embed Design
        embed = discord.Embed(
            title="🎮 XO ONLINE GAME & ECONOMY MANUAL 🎮",
            description="Welcome to the Tic-Tac-Toe system! Below is the complete guide and list of available commands.",
            color=discord.Color.from_rgb(255, 215, 0) # 🟡 Premium Gold Color
        )

        # 💰 Economy & Banking Section
        embed.add_field(
            name="🪙 Economy & Wallet System",
            value=(
                "• tbal — View your wallet, bank balance, and win/lost gameplay statistics.\n"
                "• Tbank <amount or all> — Deposit your coins safely into the bank.\n"
                "• Tout <amount or all> — Withdraw your coins from the bank back to your wallet.\n"
                "• tp @user <amount> — Transfer coins securely to another player."
            ),
            inline=False
        )

        # ⚔️ Competitive Game Section
        embed.add_field(
            name="⚔️ Matchmaking & Wagers",
            value=(
                "• txo @user <bet> — Challenge a friend to a high-stakes Tic-Tac-Toe match.\n"
                "• vsnpc <bet or all> — Bet your coins and challenge our smart AI NPC."
            ),
            inline=False
        )

        # 📖 How to Play Section
        embed.add_field(
            name="📖 How to Play Tic-Tac-Toe",
            value=(
                "1. Once a match begins, the active grid board will be displayed.\n"
                "2. When it is your turn, type a number from 1 to 9 directly in the chat to place your mark:\n"
                "   ```\n"
                "   1 | 2 | 3\n"
                "   ---------\n"
                "   4 | 5 | 6\n"
                "   ---------\n"
                "   7 | 8 | 9\n"
                "   ```\n"
                "3. In the event of a Tie, the game automatically starts a new round until a definitive winner emerges.\n"
                "4. Every turn has a 5-minute limit. Going AFK will trigger an automatic defeat."
            ),
            inline=False
        )

        # Set bot thumbnail and user footer for a professional finish
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name} • XO Bot System 2026", 
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
