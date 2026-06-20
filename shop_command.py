import discord
from discord.ext import commands, tasks
import random
from threading import Lock

# 📦 ការកំណត់ទិន្នន័យទំនិញ ភាគរយ និងតម្លៃ (បងអាចប្ដូរឈ្មោះទំនិញ និងរូប Emoji ក្នុង "" បាន)
ITEMS_POOL = {
    "Common": {"name": "Wooden Shield 🪵", "chance": 99, "price": 2000000, "color": discord.Color.light_gray()},
    "Rare": {"name": "Iron Sword ⚔️", "chance": 60, "price": 3000000, "color": discord.Color.blue()},
    "Epic": {"name": "Shadow Cloak 🔮", "chance": 50, "price": 6000000, "color": discord.Color.purple()},
    "Legendary": {"name": "Dragon Relic 👑", "chance": 20, "price": 10000000, "color": discord.Color.orange()},
    "Mythic": {"name": "⚡ GODSLAYER AURA ⚡", "chance": 1, "price": 30000000, "color": discord.Color.from_rgb(139, 0, 0)} # 🔴 ក្រហមក្រម៉ៅស្អាតខ្លាំង
}

class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_item_tier = "Common" # ហាងចាប់ផ្ដើមដំបូងដោយទំនិញ Common
        self.shop_lock = Lock()
        self.rotate_shop_items.start() # ចាប់ផ្ដើមដំណើរការរង្វិលជុំ ៤ នាទីម្ដង

    def cog_unload(self):
        self.rotate_shop_items.cancel()

    # 🔄 រង្វិលជុំគណនាប្ដូរទំនិញក្នុងហាងរៀងរាល់ ៤ នាទីម្ដង
    @tasks.loop(minutes=4.0)
    async def rotate_shop_items(self):
        tiers = list(ITEMS_POOL.keys())
        # គណនាភាគរយ Weights ផ្អែកលើ Chance ដែលបងបានកំណត់
        weights = [ITEMS_POOL[t]["chance"] for t in tiers]
        
        with self.shop_lock:
            self.current_item_tier = random.choices(tiers, weights=weights, k=1)[0]
        print(f"🔄 [Shop Rotation] Current available item updated to: {self.current_item_tier}")

    @commands.command(name="t/shop")
    async def show_shop(self, ctx):
        # ហៅការទាញយកកូដ Format លេខរាប់លានមកប្រើ (ទាញចេញពី main.py)
        from main import format_number, emoji, get_balance, save_data
        
        with self.shop_lock:
            tier = self.current_item_tier
            
        item_data = ITEMS_POOL[tier]
        item_name = item_data["name"]
        item_price = item_data["price"]
        item_color = item_data["color"]
        item_chance = item_data["chance"]

        # 👑 បង្កើតកាត Embed ទៅតាមកម្រិត Tier (កាន់តែថ្លៃ កាន់តែស្អាត)
        embed = discord.Embed(title="🏪 LIMITED-TIME GACHA SHOP 🏪", color=item_color)
        
        # រចនាការតុបតែងបន្ថែមជាពិសេសសម្រាប់ Tier ធំៗ
        if tier == "Mythic":
            embed.set_author(name="🔥 MYTHICAL ITEM DETECTED 🔥", icon_url="https://imgur.com")
            embed.description = "🚨 🚨 ULTRA RARE LIGHTNING SALE! 🚨 🚨\nAn item of god-like power has appeared in the market! It will vanish in 4 minutes!"
        elif tier == "Legendary":
            embed.set_author(name="✨ LEGENDARY ITEM AVAILABLE ✨")
            embed.description = "🌟 *A legendary treasure has been unearthed! Grab it before it's gone!*"
        else:
            embed.description = "Welcome to the shop! Items here rotate automatically every 4 minutes. Check back often for rarer loot!"

        # 📊 បង្ហាញព័ត៌មានទំនិញដែលកំពុងលក់
        embed.add_field(
            name="📦 Active Item on Sale",
            value=f"**Name:** {item_name}\n**Rarity Tier:** `{tier}`\n**Spawn Chance:** `{item_chance}%`",
            inline=False
        )
        
        embed.add_field(
            name="💰 Price Tag",
            value=f"**Cost:** {format_number(item_price)} {emoji}",
            inline=False
        )

        # 🛒 បង្កើតប៊ូតុងសម្រាប់ចុចទិញទំនិញ
        class BuyButtonView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=30.0)
                self.author = author
                
            @discord.ui.button(label=f"Buy Now ({format_number(item_price)})", style=discord.ButtonStyle.success, emoji="🛒")
            async def buy_item(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != self.author.id:
                    await interaction.response.send_message("❌ You cannot buy items from someone else's shop menu!", ephemeral=True)
                    return
                user_bal = get_balance(interaction.user.id)
                
                if user_bal["wallet"] < item_price:
                    await interaction.response.send_message(f"❌ Transaction Failed! You don't have enough coins in your wallet. Need {format_number(item_price)} {emoji}!", ephemeral=True)
                    return
                
                # កាត់លុយ និងរក្សាទុកទិន្នន័យ
                user_bal["wallet"] -= item_price
                
                # 🛡️ បន្ថែមប្រព័ន្ធដឹងថាខ្លួនឯងទិញបានអី (Inventory System) ទៅថ្ងៃមុខ
                if "inventory" not in user_bal:
                    user_bal["inventory"] = []
                user_bal["inventory"].append(item_name)
                
                save_data()
                button.disabled = True
                
                # បង្កើតកាត Embed ជោគជ័យ
                success_embed = discord.Embed(title="🎉 PURCHASE SUCCESSFUL! 🎉", color=discord.Color.green())
                success_embed.description = (
                    f"Congratulations {interaction.user.mention}!\n"
                    f"Successfully bought {item_name} (`{tier}`) for {format_number(item_price)} {emoji}.\n\n"
                    f"📉 Remaining Wallet Balance: {format_number(user_bal['wallet'])} {emoji}"
                )
                await interaction.response.edit_message(embed=success_embed, view=self)

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            
        embed.set_footer(text="Shop rotation resets every 4 minutes • XO Economy 2026")
        
        view = BuyButtonView(author=ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
