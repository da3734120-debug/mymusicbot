import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread

# ==================== ១. WEB SERVER សម្រាប់ KEEP ALIVE ២៤/៧ ====================
app = Flask('')

@app.route('/')
def home():
    return "TwT Music Bot is Online 24/7 WITHOUT LAVALINK!"

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

# ការកំណត់សម្រាប់ទាញយកសំឡេងពី YouTube (ទម្រង់ថ្មីឆ្នាំ ២០២៦)
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f"=== {bot.user.name} (Direct YT Edition) ONLINE ===")

# ==================== ៣. DISCORD MUSIC COMMANDS (ចាក់ផ្ទាល់មិនឆ្លង Node) ====================
@bot.command(name="p")
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ អ្នកត្រូវតែចូលក្នុង Voice Channel សិន!")
        
    destination = ctx.author.voice.channel
    
    # ឱ្យ Bot ចូលក្នុង Voice Room ភ្លាមៗនៅពេលវាយបញ្ជា
    if not ctx.voice_client:
        vc = await destination.connect()
    else:
        vc = ctx.voice_client

    await ctx.send(f"🔍 កំពុងស្វែងរកបទចម្រៀង៖ {search}...")

    # ទាញយក Link សំឡេងដោយប្រើ yt-dlp
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
        try:
            info = ytdl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
        except Exception as e:
            return await ctx.send("❌ មិនអាចទាញយកបទចម្រៀងនេះបានទេ (YouTube Block IP របស់ Host)។")

    # បញ្ឈប់ភ្លេងចាស់ បើមានកំពុងលេង
    if vc.is_playing():
        vc.stop()

    # ដំណើរការចាក់ភ្លេងចូលក្នុង Room ដោយប្រើ FFmpeg 
    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
    vc.play(source)
    
    embed = discord.Embed(
        description=f"🟢 កំពុងចាក់បទ៖ **{title}**", 
        color=0x1ed760
    )
    await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
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

# ==================== ៤. ដំណើរការ APPLICATION ====================
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ Error: DISCORD_TOKEN variable is missing in Railway Variables!")
