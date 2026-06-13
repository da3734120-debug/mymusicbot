import discord
from discord.ext import commands
import wavelink
import os
from flask import Flask
from threading import Thread

# ==================== ១. បង្កើត WEB SERVER សម្រាប់ KEEP ALIVE ២៤/៧ ====================
app = Flask('')

@app.route('/')
def home():
    return "TwT Music Lavalink Bot is Online 24/7!"

def run_web():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==================== ២. SETUP INTENTS និង BOT ====================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True # ដាច់ខាតត្រូវតែបើក ដើម្បីឱ្យ Lavalink ស្គាល់សម្លេង

bot = commands.Bot(command_prefix="T!", intents=intents)
# ==================== ៣. ប្រព័ន្ធតភ្ជាប់ទៅកាន់ម៉ាស៊ីនចាក់ YOUTUBE (LAVALINK) ====================
async def connect_nodes():
    await bot.wait_until_ready()
    
    node = wavelink.Node(
        uri="lavalink-2026-production-df10.up.railway.app:8080", # 🟢 ដូរមកកាន់ Port 8080 របស់ម៉ាស៊ីនថ្មី
        password="youshallnotpass"
    )
    await wavelink.Pool.connect(nodes=[node], client=bot)

@bot.event
async def on_ready():
    print(f"=== {bot.user.name} (Lavalink Edition) ONLINE ===")
    bot.loop.create_task(connect_nodes())

@bot.event
async def on_wavelink_node_ready(payload):
    print("✅ ម៉ាស៊ីន Lavalink Node ភ្ជាប់ជោគជ័យ និងត្រៀមខ្លួនចាក់ YouTube រួចរាល់ហើយ!")
@bot.command(name="p")
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ អ្នកត្រូវតែចូលក្នុង Voice Channel សិន!")
        
    destination = ctx.author.voice.channel
    
    # ភ្ជាប់ Bot ចូល Voice Channel
    if not ctx.voice_client:
        player: wavelink.Player = await destination.connect(cls=wavelink.Player)
    else:
        player: wavelink.Player = ctx.voice_client
        
    # បញ្ជាឱ្យ Lavalink ទៅអូសទាញយកបទចម្រៀងពីលីង YouTube មកភ្លាមៗ
    tracks: wavelink.Search = await wavelink.Playable.search(search)
    if not tracks:
        return await ctx.send("❌ រកមិនឃើញបទចម្រៀង ឬលីង YouTube នេះទេ!")
        
    # ✅ ចាប់យកបទទី ១ ចេញពីលីង YouTube ដែលរកឃើញមកចាក់ភ្លាម
    track = tracks[0] 
    await player.play(track)
    
    embed = discord.Embed(
        description=f"🟢 កំពុងចាក់បទពី YouTube: **[{track.title}]({track.uri})**", 
        color=0x1ed760
    )
    await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        await ctx.voice_client.skip()
        await ctx.send("⏭️ បានរំលងចម្រៀងចោលជោគជ័យ!")
    else:
        await ctx.send("❌ គ្មានបទចម្រៀងកំពុងលេងទេ។")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 បានបិទ និងចាកចេញពី Voice Channel រួចរាល់។")
    else:
        await ctx.send("❌ Bot មិនទាន់បានចូល Voice Channel ឡើយ។")
        # ==================== ៥. ដំណើរការ APPLICATION រួមគ្នាជាមួយ WEB PORT ====================
keep_alive()

# ប្រព័ន្ធនឹងទាញយក Token ពី Variables របស់ Railway ឱ្យត្រូវនឹងទម្រង់របស់បង
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Error: DISCORD_TOKEN variable is missing in Railway Variables!")
    
