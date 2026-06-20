import discord
from discord.ext import commands, tasks
import random
from threading import Lock
import main  # 🔌 ហៅចូល main ចំៗដើម្បីកាត់លុយឱ្យរត់ចូល Database ធំ

# 📦 ការកំណត់ទិន្នន័យទំនិញ តម្លៃ និងពណ៌ ANSI សម្រាប់ប្រើក្នុង Code Block
ITEMS_POOL = {
    "Common": {
        "name": "Wooden Shield 🪵", 
        "chance": 99, 
        "price": 2000000, 
        "color": discord.Color.light_gray(),
        "ansi_name": " [1;30m[Common] [0m Wooden Shield 🪵"  # ⚪ ពណ៌ប្រផេះ
    },
    "Rare": {
        "name": "Iron Sword ⚔️", 
        "chance": 60, 
        "price": 3000000, 
        "color": discord.Color.blue(),
        "ansi_name": " [1;34m[Rare] [0m Iron Sword ⚔️"      # 🔵 ពណ៌ខៀវ
    },
    "Epic": {
        "name": "Shadow Cloak 🔮", 
        "chance": 50, 
        "price": 6000000, 
        "color": discord.Color.purple(),
        "ansi_name": " [1;35m[Epic] [0m Shadow Cloak 🔮"      # 🟣 ពណ៌ស្វាយ
    },
    "Legendary": {
        "name": "Dragon Relic 👑", 
        "chance": 20, 
        "price": 10000000, 
        "color": discord.Color.orange(),
        "ansi_name": " [1;33m[Legendary] [0m Dragon Relic 👑" # 🟡 ពណ៌លឿងមាស
    },
    "Mythic": {
        "name": "⚡ GODSLAYER AURA ⚡", 
        "chance": 1, 
        "price": 30000000, 
        "color": discord.Color.from_rgb(139, 0, 0),
        "ansi_name": " [1;31m[Mythic]⚡ GODSLAYER AURA ⚡ [0m" # 🔴 ពណ៌ក្រហមដិតឡូយខ្លាំង
    }
}

class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_item_tier = "Common"
        self.shop_lock = Lock()
        self.rotate_shop_items.start()

    def cog_unload(self):
        self.rotate_shop_items.cancel()

    # 🔄 រង្វិលជុំប្ដូរស្តុកទំនិញរៀងរាល់ ៤ នាទីម្ដង
    @tasks.loop(minutes=4.0)
    async def rotate_shop_items(self):
        tiers = list(ITEMS_POOL.keys())
        weights = [ITEMS_POOL[t]["chance"] for t in tiers]
        
        with self.shop_lock:
            # គណនាជ្រើសរើសទំនិញ ១ ដែលមានស្តុកលក់
            chosen = random.choices(tiers, weights=weights, k=1)
            self.current_item_tier = chosen[0]
        print(f"🔄 [Shop Stock Updated] Active Stock: {self.current_item_tier}")

    @commands.command(name="t/shop")
    async def show_shop(self, ctx):
        with self.shop_lock:
            active_tier = self.current_item_tier
            
        active_data = ITEMS_POOL[active_tier]
        embed = discord.Embed(title="🏪 MAIN STREET GACHA MARKET 🏪", color=active_data["color"])
        
        if active_tier == "Mythic":
            embed.set_author(name="🔥 MYTHICAL STOCK DETECTED 🔥")
            embed.description = "🚨 ULTRA RARE DROP IN STOCK! 🚨\nThe mythical stock has spawned! It will vanish in 4 minutes!"
        elif active_tier == "Legendary":
            embed.set_author(name="✨ LEGENDARY STOCK AVAILABLE ✨")
            embed.description = "🌟 *A legendary item has arrived in the display cabinet!*"
        else:
            embed.description = "Welcome to the market! Below is the full catalog of items. Only one item has stock at a time (Rotates every 4 minutes)!"

        # 📋 បង្ហាញទំនិញទាំងអស់ជាជួរៗ និងមានពណ៌ខុសៗគ្នាតាម ANSI Code (លាក់ % ចោលទាំងស្រុង)
        catalog_lines = []
        for tier_name, data in ITEMS_POOL.items():
            stock_status = "🟢 [IN STOCK]" if tier_name == active_tier else "🔴 [OUT OF STOCK]"
            catalog_lines.append(f"{data['ansi_name']}\n   Price: {main.format_number(data['price'])} {main.emoji} | {stock_status}\n")
            
        full_catalog = "\n".join(catalog_lines)
        embed.add_field(
            name="📋 Full Item Catalog",
            value=f"```ansi\n{full_catalog}```", # 👈 ប្រើ ansi block ដើម្បីឱ្យអក្សរចេញពណ៌ខុសគ្នាលើ Discord
            inline=False
        )

        # 🔘 បង្កើតផ្ទាំងប៊ូតុងគ្រប់គ្រងស្តុក
        class ShopStockView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=45.0)
                self.author = author
                self.setup_buttons()

            def setup_buttons(self):
                # បង្កើតប៊ូតុងទៅតាមទំនិញទាំងអស់ជាជួរ
                for tier_name, data in ITEMS_POOL.items():
                    is_active = (tier_name == active_tier)
                    
                    if is_active:
                        # បើមានស្តុក៖ ប៊ូតុងពណ៌បៃតង ចុចទិញបាន
                        btn = discord.ui.Button(
                            label=f"Buy Now: {tier_name}", 
                            style=discord.ButtonStyle.success, 
                            custom_id=f"buy_{tier_name}",
                            emoji="🛒"
                        )
                    else:
                        # បើអស់ស្តុក៖ ប៊ូតុងពណ៌ក្រហម និងក្រៀម (Disabled) ចុចមិនបាន
                        btn = discord.ui.Button(
                            label=f"Out of Stock: {tier_name}", 
                            style=discord.ButtonStyle.danger, 
                            disabled=True,
                            custom_id=f"nos_{tier_name}"
                        )
                        
                    btn.callback = self.make_callback(tier_name, data["price"], data["name"])
                    self.add_item(btn)

            def make_callback(self, tier_name, price, item_full_name):
                async def callback(interaction: discord.Interaction):
                    if interaction.user.id != self.author.id:
                        await interaction.response.send_message("❌ You cannot interact with this shop menu!", ephemeral=True)
                        return
                    
                    # 🔒 ចាប់ផ្ដើមទាញយកគណនីមកកាត់លុយ និងសរសេរចូល Database ធំរបស់ main.py ចំៗ
                    uid = str(interaction.user.id)
                    user_bal = main.get_balance(interaction.user.id)
                    
                    # ទាញទិន្នន័យចុងក្រោយបង្អស់ពី main.user_balances មកផ្ទៀងផ្ទាត់
                    current_wallet = main.user_balances[uid]["wallet"]
                    
                    if current_wallet < price:
                        await interaction.response.send_message(f"❌ Purchase Failed! You need {main.format_number(price)} {main.emoji} in your wallet!", ephemeral=True)
                        return
                    
                    # 📉 កាត់លុយចេញពីកាបូបធំនៅក្នុង main.py
                    main.user_balances[uid]["wallet"] -= price
                    
                    # បន្ថែមទំនិញចូលកាតាបសន្សំឥវ៉ាន់ (Inventory)
                    if "inventory" not in main.user_balances[uid]:
                        main.user_balances[uid]["inventory"] = []
                    main.user_balances[uid]["inventory"].append(item_full_name)
                    
                    # 💾 រក្សាទុកទិន្នន័យចូល balances.json ភ្លាមៗ
                    main.save_data()
                    
                    # បិទប៊ូតុងទាំងអស់ក្រោយទិញរួចរាល់
                    for child in self.children:
                        child.disabled = True
                        
                    success_embed = discord.Embed(title="🎉 TRANSACTION SUCCESSFUL! 🎉", color=discord.Color.green())
                    success_embed.description = (
                        f"Thank you for your purchase {interaction.user.mention}!\n"
                        f"Successfully acquired {item_full_name} (`{tier_name}`) for {main.format_number(price)} {main.emoji}.\n\n"
                        f"💰 Balance updated in tbal! Remaining Wallet: {main.format_number(main.user_balances[uid]['wallet'])} {main.emoji}"
                    )
                    await interaction.response.edit_message(embed=success_embed, view=self)
                    
                return callback

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Stock rotation refreshes every 4 minutes • XO Market 2026")
        
        view = ShopStockView(author=ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
