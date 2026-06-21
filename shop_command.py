import discord
from discord.ext import commands, tasks
import random
from threading import Lock
import json
import os
import main

# 📦 ការកំណត់ទិន្នន័យ Skin តម្លៃ និងពណ៌ (ស្ទីល Grow a Garden)
SKINS_POOL = {
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
        tiers = list(SKINS_POOL.keys())
        weights = [SKINS_POOL[t]["chance"] for t in tiers]
        with self.shop_lock:
            self.current_item_tier = random.choices(tiers, weights=weights, k=1)[0]
        print(f"🔄 [Shop Stock Updated] Active Stock: {self.current_item_tier}")

    @commands.command(name="t/shop")
    async def show_shop(self, ctx):
        with self.shop_lock:
            active_tier = self.current_item_tier
            
        active_data = SKINS_POOL[active_tier]
        uid = str(ctx.author.id)
        user_bal = main.get_balance(ctx.author.id)
        
        embed = discord.Embed(
            title="🏪 GROW GARDEN SKIN MARKET 🏪", 
            description="Purchase exclusive skins to customize your profile color! Stock rotates every 4 minutes.",
            color=active_data["color"]
        )

        for tier_name, data in SKINS_POOL.items():
            is_active = (tier_name == active_tier)
            stock_status = "🟢 **IN STOCK**" if is_active else "🔴 **OUT**"
            
            # ផ្ទៀងផ្ទាត់មើលថាធ្លាប់ទិញហើយឬនៅ
            unlocked = "inventory" in user_bal and data["name"] in user_bal["inventory"]
            owned_status = " 🔒 [Locked]" if not unlocked else " ✅ [Owned]"
            price_fmt = main.format_number(data['price'])
            
            embed.add_field(
                name=f"{data['emoji']} {tier_name} Tier{owned_status}",
                value=f"• Skin: {data['name']}\n• Price: {price_fmt} {main.emoji}\n• Status: {stock_status}",
                inline=False
            )

        class ShopStockView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=45.0)
                self.author = author
                self.setup_buttons()

            def setup_buttons(self):
                for tier_name, data in SKINS_POOL.items():
                    is_active = (tier_name == active_tier)
                    has_skin = "inventory" in user_bal and data["name"] in user_bal["inventory"]
                    is_equipped = "active_skin" in user_bal and user_bal["active_skin"] == data["name"]
                    
                    if is_equipped:
                        btn = discord.ui.Button(label="Using", style=discord.ButtonStyle.secondary, disabled=True, custom_id=f"use_{tier_name}")
                    elif has_skin:
                        btn = discord.ui.Button(label="Equip", style=discord.ButtonStyle.primary, custom_id=f"eq_{tier_name}")
                    elif is_active:
                        btn = discord.ui.Button(label=f"Buy {tier_name}", style=discord.ButtonStyle.success, custom_id=f"buy_{tier_name}", emoji="🛒")
                    else:
                        btn = discord.ui.Button(label="Out", style=discord.ButtonStyle.danger, disabled=True, custom_id=f"nos_{tier_name}")
                        
                    btn.callback = self.make_callback(tier_name, data["price"], data["name"], has_skin)
                    self.add_item(btn)

            def make_callback(self, tier_name, price, item_full_name, has_skin):
                async def callback(interaction: discord.Interaction):
                    if interaction.user.id != self.author.id:
                        await interaction.response.send_message("❌ You cannot interact with this menu!", ephemeral=True)
                        return
                    
                    uid = str(interaction.user.id)
                    data_dict = main.load_data_from_file()
                    
                    if uid not in data_dict:
                        data_dict[uid] = {"wallet": 100, "bank": 0, "win": 0, "lost": 0, "inventory": ["Normal ✨"], "active_skin": "Normal ✨"}

                    # 🔄 ករណីចុចពាក់ Skin (Equip Function)
                    if has_skin:
                        data_dict[uid]["active_skin"] = item_full_name
                        with open(main.DATA_FILE, "w") as f: json.dump(data_dict, f, indent=4)
                        main.user_balances = data_dict
                        await interaction.response.send_message(f"✅ Successfully equipped {item_full_name} skin!", ephemeral=True)
                        return

                    # 🛒 ករណីចុចទិញ Skin ថ្មី (Buy Function)
                    if data_dict[uid]["wallet"] < price:
                        await interaction.response.send_message(f"❌ You need {main.format_number(price)} {main.emoji} to buy this skin!", ephemeral=True)
                        return
                    
                    data_dict[uid]["wallet"] -= price
                    data_dict[uid]["inventory"].append(item_full_name)
                    data_dict[uid]["active_skin"] = item_full_name
                    
                    with open(main.DATA_FILE, "w") as f: json.dump(data_dict, f, indent=4)
                    main.user_balances = data_dict
                    
                    for child in self.children: child.disabled = True
                    success_embed = discord.Embed(title="🎉 SKIN UNLOCKED! 🎉", color=discord.Color.green())
                    success_embed.description = f"Congratulations! You unlocked and equipped {item_full_name}!\nYour profile color has been updated globally!"
                    await interaction.response.edit_message(embed=success_embed, view=self)
                    
                return callback

        if self.bot.user.avatar: embed.set_thumbnail(url=self.bot.user.avatar.url)
        view = ShopStockView(author=ctx.author)
        await ctx.send(embed=embed, view=view)

  @commands.command(name="t/inventory")
    async def show_inventory(self, ctx):
        user_bal = main.get_balance(ctx.author.id)
        raw_skins = user_bal.get("inventory", ["Normal ✨"])
        active = user_bal.get("active_skin", "Normal ✨")
        
        # 🛡️ ជួសជុលធំ (Anti-Duplicate)៖ បម្លែងទៅជា set រួចបម្លែងមក list វិញ ដើម្បីលុបទិន្នន័យជាន់គ្នាចោលទាំងអស់ ការពារ Error 400 Bad Request
        skins = list(set(raw_skins))
        
        # ប្រសិនបើ active skin ជាប្រភេទ List ដោយសារ Bug ចាស់ គឺទាញយកតែតួអក្សរដំបូងមកប្រើ
        if isinstance(active, list) and len(active) > 0:
            active = active[0]
        elif isinstance(active, list):
            active = "Normal ✨"
            
        embed = discord.Embed(
            title=f"🎒 {ctx.author.display_name}'s Wardrobe", 
            description="Select a skin below to change your global theme color:", 
            color=discord.Color.blue()
        )
        
        class InventoryView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=60.0)
                self.author = author
                self.setup_select()

            def setup_select(self):
                # បង្កើតជម្រើសដោយសុវត្ថិភាព គ្មានឈ្មោះជាន់គ្នា
                options = [discord.SelectOption(label=s, value=s, description="Click to equip this skin theme", default=(s == active)) for s in skins]
                select = discord.ui.Select(placeholder="Choose a skin to wear...", options=options)
                
                async def select_callback(interaction: discord.Interaction):
                    if interaction.user.id != self.author.id: 
                        await interaction.response.send_message("❌ You cannot change someone else's skin!", ephemeral=True)
                        return
                    
                    chosen_skin = select.values[0] # ទាញយកតម្លៃ String ជម្រើសដំបូងបង្អស់
                    data_dict = main.load_data_from_file()
                    uid = str(interaction.user.id)
                    
                    if uid in data_dict:
                        data_dict[uid]["active_skin"] = chosen_skin
                        with open(main.DATA_FILE, "w") as f: 
                            json.dump(data_dict, f, indent=4)
                        main.user_balances = data_dict
                    
                    await interaction.response.send_message(f"✅ Skin changed to {chosen_skin}!", ephemeral=True)
                    
                select.callback = select_callback
                self.add_item(select)
                
        view = InventoryView(author=ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
