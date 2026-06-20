import discord
from discord.ext import commands, tasks
import random
from threading import Lock
import json
import os
import main  # 🔌 ហៅចូល main ដើម្បីទាញយកទម្រង់រៀបចំ និងអថេរ

# 📦 ការកំណត់ទិន្នន័យទំនិញ តម្លៃ និងពណ៌កាត (ស្ទីលហ្គេម Grow a Garden)
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
            self.current_item_tier = chosen[0]
        print(f"🔄 [Shop Stock Updated] Active Stock: {self.current_item_tier}")

    @commands.command(name="t/shop")
    async def show_shop(self, ctx):
        with self.shop_lock:
            active_tier = self.current_item_tier
            
        active_data = ITEMS_POOL[active_tier]
        
        # 👑 បង្កើតកាត Embed ធំប្រណីតពណ៌ទៅតាមទំនិញដែលមានស្តុក
        embed = discord.Embed(
            title="🏪 GROW GARDEN MARKET 🏪", 
            description="Welcome to the shop catalog! Items rotate automatically every 4 minutes. Grab them while they are in stock!",
            color=active_data["color"]
        )
        
        if active_tier == "Mythic":
            embed.set_author(name="🚨 ULTRA RARE DROPS DETECTED 🚨")
        else:
            embed.set_author(name=f"✨ Active Stock Sale: {active_tier} ✨")

        # 📋 ជួសជុល៖ រៀបចំបង្កើតជាកូនប្រអប់ស្អាតៗ បំបែកពីគ្នា (លុបប្រអប់ ANSI ចោល)
        for tier_name, data in ITEMS_POOL.items():
            is_active = (tier_name == active_tier)
            stock_icon = "🟢 **IN STOCK**" if is_active else "🔴 **OUT**"
            price_fmt = main.format_number(data['price'])
            
            # បង្កើត Field ជាប្រអប់កូនៗរៀបតាមជួរ Grid យ៉ាងស្អាត
            embed.add_field(
                name=f"{data['emoji']} {tier_name} Tier",
                value=f"**Item:** {data['name']}\n**Price:** {price_fmt} {main.emoji}\n**Status:** {stock_status}",
                inline=True # 👈 កំណត់ឱ្យរៀបជាជួរផ្ដេកទន្ទឹមគ្នាលើ PC និងប្រអប់ស្អាតលើទូរស័ព្ទ
            )

        # 🔘 ផ្ទាំងប៊ូតុងបញ្ជាទិញរៀបជួរដេញតាមប្រអប់ខាងលើ
        class ShopStockView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=45.0)
                self.author = author
                self.setup_buttons()

            def setup_buttons(self):
                # រៀបប៊ូតុងចុចទិញចំនួន ៥ ឱ្យត្រូវតាមលំដាប់ទំនិញទាំង ៥ ខាងលើ
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

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Shop rotation resets every 4 minutes • Grow Garden 2026")
        
        view = ShopStockView(author=ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
