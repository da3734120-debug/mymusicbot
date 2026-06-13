import discord
from discord.ext import commands
import wavelink
import os
from flask import Flask
from threading import Thread

# ==================== ១. WEB SERVER សម្រាប់ KEEP ALIVE ២ POUR ៤/៧ ====================
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
intents.voice_states = True 

bot = commands.Bot(command_prefix="T!", intents=intents)

# ==================== ៣. ប្រព័ន្ធតភ្ជាប់ទៅកាន់ម៉ាស៊ីនចាក់ភ្លេង ====================
async def connect_nodes():
    await bot.wait_until_ready()
    
    # ✅ ភ្ជាប់ទៅកាន់ម៉ាស៊ីន Lavalink ផ្ទាល់ខ្លួនក្នុង Railway ដោយប្រើប្រព័ន្ធ Private Networking
    node = wavelink.Node(
        uri="http://railway.internal",  # ឈ្មោះ Private Domain របស់ Railway
        password="youshallnotpass"
    )
    await wavelink.Pool.connect(nodes=[node], client=bot)

@bot.event
async def on_ready():
    print(f"=== {bot.user.name} (Lavalink Edition) ONLINE ===")
    bot.loop.create_task(connect_nodes())

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"✅ ម៉ាស៊ីន Lavalink Node [{payload.node.identifier}] ភ្ជាប់ជោគជ័យ និងត្រៀមខ្លួនរួចរាល់!")

# ==================== ៤. DISCORD MUSIC COMMANDS (FULL) ====================
@bot.command(name="p")
async def play(ctx, *, search: str):
    # ១. ពិនិត្យមើលថាតើអ្នកប្រើប្រាស់នៅក្នុង Voice Room ឬអត់
    if not ctx.author.voice:
        return await ctx.send("❌ អ្នកត្រូវតែចូលក្នុង Voice Channel សិន!")
        
    destination = ctx.author.voice.channel
    
    # ២. ស្វែងរកបទចម្រៀងតាមរយៈប្រព័ន្ធ 'ytsearch:' មុននឹងឱ្យ Bot ចូល Room
    tracks = await wavelink.Playable.search(f"ytsearch:{search}")
    if not tracks:
        return await ctx.send("❌ រកមិនឃើញបទចម្រៀង ឬលីងនេះទេ!")
        
    # ៣. ចាប់យកបទចម្រៀងដំបូងគេបង្អស់ (First Track) ពីក្នុងប្រអប់លទ្ធផល
    track = tracks[0] 
    
    # ៤. បញ្ជាឱ្យ Bot ចូលទៅក្នុង Voice Channel បើវាមិនទាន់ចូល
    if not ctx.voice_client:
        player: wavelink.Player = await destination.connect(cls=wavelink.Player)
    else:
        player: wavelink.Player = ctx.voice_client
        
    # ៥. ដំណើរការចាក់ភ្លេង
    await player.play(track)
    
    # ៦. បង្ហាញផ្ទាំង Embed ស្អាតៗនៅក្នុង Chat 
    embed = discord.Embed(
        description=f"🟢 កំពុងចាក់បទ៖ **[{track.title}]({track.uri})**", 
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

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Error: DISCORD_TOKEN variable is missing in Railway Variables!")
