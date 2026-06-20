import discord
from discord.ext import commands, tasks
import random
from threading import Lock
import json
import os
import main  # 🔌 តភ្ជាប់ទៅ main.py ចំៗដើម្បីការពារ Error

# 📦 ទិន្នន័យទំនិញ តម្លៃ និងរូបសញ្ញា (ស្ទីលហ្គេម Grow a Garden)
ITEMS_POOL = {
    "Common": {"name": "Wooden Shield 🪵", "chance": 99, "price": 2000000, "color": discord.Color.light_gray(), "emoji": "⚪"},
    "Rare": {"name": "Iron Sword ⚔️", "chance": 60, "price": 3000000, "color": discord.Color.blue(), "emoji": "🔵"},
    "Epic": {"name": "Shadow Cloak 🔮", "chance": 50, "price": 6000000, "color": discord.Color.purple(), "emoji": "🔮"},
    "Legendary": {"name": "Dragon Relic 👑", "chance": 20, "price": 10000000, "color": discord.Color.orange(), "emoji": "👑"},
    "Mythic": {"name": "⚡ GODSLAYER AURA ⚡", "chance": 1, "price": 30000000, "color": discord.Color.from_rgb(139, 0, 0), "emoji": "🔥"}
}

class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_item_tier = "Common"
        self.shop_lock = Lock()
        self.rotate_shop_items.start()

    def cog_unload(self):
        self.rotate_shop_items.cancel()

    @tasks.loop(minutes=4.0)
    async def rotate_shop_items(self):
        tiers = list(ITEMS_POOL.keys())
        weights = [ITEMS_POOL[t]["chance"] for t in tiers]
        with self.shop_lock:
            chosen = random.choices(tiers, weights=weights, k=1)
            self.current_item_tier = chosen[0] # កែសម្រួលចំណុចអាន String ចំៗ
        print(f"🔄 [Shop Stock Updated] Active Stock: {self.current_item_tier}")

    @commands.command(name="t/shop")
    async def show_shop(self, ctx):
        with self.shop_lock:
            active_tier = self.current_item_tier
            
        active_data = ITEMS_POOL[active_tier]
        
        # 👑 បង្កើតកាត Embed ស្អាតប្រណីតកម្រិត Premium ដូច Grow a Garden UI
        embed = discord.Embed(
            title="🏪 GROW GARDEN SEED & GEAR MARKET 🏪", 
            description="Welcome to the shop market! Stock refreshes every 4 minutes.",
            color=active_data["color"]
        )
        embed.set_author(name="✨ AUTOMATED GACHA MARKET UP-TIME ✨")

        # 📋 បង្កើតជាកូនប្រអប់ស្អាតៗ បំបែកពីគ្នា (លុបប្រអប់ ANSI ខ្មៅវែងចាស់ចោល)
        for tier_name, data in ITEMS_POOL.items():
            is_active = (tier_name == active_tier)
            stock_status = "🟢 **IN STOCK**" if is_active else "🔴 **OUT**"
            price_fmt = main.format_number(data['price'])
            
            embed.add_field(
                name=f"{data['emoji']} {tier_name} Tier",
                value=f"• Item: {data['name']}\n• Price: {price_fmt} {main.emoji}\n• Status: {stock_status}",
                inline=False # កំណត់ឱ្យចុះបន្ទាត់រៀបប្រអប់ស្អាតត្រូវទំហំទូរស័ព្ទជានិច្ច
            )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name} • Market Version 2026", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        # 🔘 ថ្នាក់បង្កើតប៊ូតុងបញ្ជាទិញរៀបជួរគ្នាយ៉ាងសមសួននៅខាងក្រោមប្រអប់
        class ShopStockView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=45.0)
                self.author = author
                self.setup_buttons()

            def setup_buttons(self):
                for tier_name, data in ITEMS_POOL.items():
                    is_active = (tier_name == active_tier)
                    if is_active:
                        btn = discord.ui.Button(label=f"Buy {tier_name}", style=discord.ButtonStyle.success, custom_id=f"buy_{tier_name}", emoji="🛒")
                    else:
                        btn = discord.ui.Button(label=f"Out", style=discord.ButtonStyle.danger, disabled=True, custom_id=f"nos_{tier_name}")
                    btn.callback = self.make_callback(tier_name, data["price"], data["name"])
                    self.add_item(btn)

            def make_callback(self, tier_name, price, item_full_name):
                async def callback(interaction: discord.Interaction):
                    if interaction.user.id != self.author.id:
                        await interaction.response.send_message("❌ You cannot interact with this shop menu!", ephemeral=True)
                        return
                    
                    uid = str(interaction.user.id)
                    db_path = main.DATA_FILE
                    data_dict = {}
                    
                    if os.path.exists(db_path):
                        try:
                            with open(db_path, "r") as f: data_dict = json.load(f)
                        except: data_dict = main.user_balances
                    else:
                        data_dict = main.user_balances

                    if uid not in data_dict:
                        data_dict[uid] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0, "inventory": []}

                    current_wallet = data_dict[uid]["wallet"]
                    if current_wallet < price:
                        await interaction.response.send_message(f"❌ Purchase Failed! You need {main.format_number(price)} {main.emoji} in your wallet!", ephemeral=True)
                        return
                    
                    data_dict[uid]["wallet"] -= price
                    if "inventory" not in data_dict[uid]:
                        data_dict[uid]["inventory"] = []
                    data_dict[uid]["inventory"].append(item_full_name)
                    
                    with open(db_path, "w") as f:
                        json.dump(data_dict, f, indent=4)
                    
                    main.user_balances = data_dict
                    
                    for child in self.children:
                        child.disabled = True
                        
                    success_embed = discord.Embed(title="🎉 TRANSACTION SUCCESSFUL! 🎉", color=discord.Color.green())
                    success_embed.description = (
                        f"Thank you for your purchase {interaction.user.mention}!\n"
                        f"Successfully acquired {item_full_name} (`{tier_name}`) for {main.format_number(price)} {main.emoji}.\n\n"
                        f"💰 Balance updated in tbal! Remaining Wallet: {main.format_number(data_dict[uid]['wallet'])} {main.emoji}"
                    )
                    await interaction.response.edit_message(embed=success_embed, view=self)
                    
                return callback

        view = ShopStockView(author=ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
