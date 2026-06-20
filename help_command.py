import discord
from discord.ext import commands

# 🔘 បង្កើតថ្នាក់ប៊ូតុងសម្រាប់ជ្រើសរើសភាសា (Language Buttons Settings)
class HelpLanguageView(discord.ui.View):
    def __init__(self, author, timeout=60.0):
        super().__init__(timeout=timeout)
        self.author = author
        self.message = None

    # 🇬🇧 ប៊ូតុងភាសាអង់គ្លេស
    @discord.ui.button(label="English 🇬🇧", style=discord.ButtonStyle.primary)
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Only the command user can switch languages!", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="🎮 XO ONLINE GAME & ECONOMY MANUAL 🎮",
            description="Welcome to the Tic-Tac-Toe system! Below is the complete guide and list of available commands.",
            color=discord.Color.from_rgb(255, 215, 0) # 🟡 ពណ៌មាស
        )
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
        embed.add_field(
            name="⚔️ Matchmaking & Wagers",
            value=(
                "• txo @user <bet> — Challenge a friend to a high-stakes Tic-Tac-Toe match.\n"
                "• vsnpc <bet or all> — Bet your coins and challenge our smart AI NPC."
            ),
            inline=False
        )
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
        if interaction.client.user.avatar:
            embed.set_thumbnail(url=interaction.client.user.avatar.url)
        embed.set_footer(text=f"Requested by {self.author.display_name} • XO Bot System 2026", icon_url=self.author.avatar.url if self.author.avatar else None)
        
        await interaction.response.edit_message(embed=embed, view=self)

    # 🇰🇭 ប៊ូតុងភាសាខ្មែរ
    @discord.ui.button(label="Cambodia 🇰🇭", style=discord.ButtonStyle.success)
    async def cambodia_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ មានតែអ្នកប្រើប្រាស់ពាក្យបញ្ជាប៉ុណ្ណោះ ទើបអាចប្ដូរភាសាបាន!", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="🎮 ផ្ទាំងណែនាំ និងរបៀបលេងហ្គេម XO ONLINE 🎮",
            description="សូមស្វាគមន៍មកកាន់ប្រព័ន្ធហ្គេម XO និងសេដ្ឋកិច្ច! ខាងក្រោមនេះជាការណែនាំ និងពាក្យបញ្ជាទាំងអស់៖",
            color=discord.Color.from_rgb(255, 215, 0) # 🟡 ពណ៌មាស
        )
        embed.add_field(
            name="🪙 ប្រព័ន្ធសេដ្ឋកិច្ច និងកាបូបលុយ (Economy System)",
            value=(
                "• tbal — ពិនិត្យមើលចំនួនកាក់ក្នុងកាបូប ធនាគារ និងស្ថិតិឈ្នះ/ចាញ់។\n"
                "• Tbank <ចំនួន ឬ all> — ដាក់កាក់ពីកាបូបផ្ញើចូលក្នុងធនាគារឱ្យមានសុវត្ថិភាព។\n"
                "• Tout <ចំនួន ឬ all> — ដកកាក់ពីធនាគារមកកាន់កាបូបលុយវិញ។\n"
                "• tp @ឈ្មោះអ្នកទទួល <ចំនួន> — ផ្ទេរកាក់ទៅឱ្យអ្នកលេងផ្សេងដោយសុវត្ថិភាព។"
            ),
            inline=False
        )
        embed.add_field(
            name="⚔️ ប្រព័ន្ធប្រកួតប្រជែងភ្នាល់កាក់ (Matchmaking)",
            value=(
                "• txo @ឈ្មោះអ្នកលេង <ចំនួនភ្នាល់> — បបួលមិត្តភក្តិប្រកួត XO ភ្នាល់កាក់យកឈ្នះចាញ់។\n"
                "• vsnpc <ចំនួនភ្នាល់ ឬ all> — ភ្នាល់កាក់ប្រកួតជាមួយម៉ាស៊ីន AI ឆ្លាតវៃ (NPC)។"
            ),
            inline=False
        )
        embed.add_field(
            name="📖 របៀបលេងហ្គេម XO (How to Play)",
            value=(
                "១. នៅពេលការប្រកួតចាប់ផ្ដើម ក្តារខៀន XO នឹងបង្ហាញឡើង។\n"
                "២. ដល់វេនបងលេង ត្រូវវាយលេខពី ១ ដល់ ៩ ចំៗ នៅក្នុង Chat ដើម្បីទម្លាក់គ្រាប់៖\n"
                "   ```\n"
                "   1 | 2 | 3\n"
                "   ---------\n"
                "   4 | 5 | 6\n"
                "   ---------\n"
                "   7 | 8 | 9\n"
                "   ```\n"
                "៣. ករណីលទ្ធផល ស្មើគ្នា (Tie) ហ្គេមនឹងចាប់ផ្ដើមទឹកថ្មីភ្លាមៗ រហូតដល់រកឃើញអ្នកឈ្នះពិតប្រាកដ។\n"
                "៤. រាល់វេនលេងនីមួយៗមានពេលកំណត់ ៥ នាទី បើទុកឱ្យហួសពេល (AFK) នឹងត្រូវចាញ់ស្វ័យប្រវត្ត។"
            ),
            inline=False
        )
        if interaction.client.user.avatar:
            embed.set_thumbnail(url=interaction.client.user.avatar.url)
        embed.set_footer(text=f"ស្នើសុំដោយ {self.author.display_name} • ប្រព័ន្ធ XO Bot 2026", icon_url=self.author.avatar.url if self.author.avatar else None)
        
        await interaction.response.edit_message(embed=embed, view=self)

    # ⏰ ប្រព័ន្ធបិទប៊ូតុងនៅពេលហួសកំណត់ (Timeout)
    async def on_timeout(self):
        try:
            for child in self.children:
                child.disabled = True
            if self.message:
                await self.message.edit(view=self)
        except:
            pass


# 📖 ថ្នាក់ពាក្យបញ្ជា T/help ចម្បង
class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="t/help")
    async def help_command(self, ctx):
        # 🔔 ផ្ទាំងដំបូងបង្អស់ពេលវាយពាក្យបញ្ជា (សួរឱ្យជ្រើសរើសភាសា)
        embed = discord.Embed(
            title="🎮 XO ONLINE BOT MENU 🎮",
            description=(
                "Please select your language below to view the command guide!\n"
                "សូមចុចជ្រើសរើសភាសានៅខាងក្រោម ដើម្បីមើលការណែនាំពីពាក្យបញ្ជា!"
            ),
            color=discord.Color.from_rgb(255, 215, 0)
        )
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="XO Bot Language Selector • 2026")

        view = HelpLanguageView(author=ctx.author, timeout=60.0)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg # រក្សាទុកសារដើម្បីងាយស្រួលបិទប៊ូតុងពេល Timeout

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
