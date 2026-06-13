import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread

# === ប្តូរមកប្រើប្រាស់ប្រព័ន្ធស្វែងរកផ្លូវ FFmpeg របស់ ffdl វិញ ===
import os
ffmpeg_path = "./bin/ffmpeg" if os.path.exists("./bin/ffmpeg") else "ffmpeg"

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

# ==================== ៣. DISCORD MUSIC COMMANDS ====================
@bot.command(name="p")
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ អ្នកត្រូវតែចូលក្នុង Voice Channel សិន!")
        
    destination = ctx.author.voice.channel
    
    if not ctx.voice_client:
        vc = await destination.connect()
    else:
        vc = ctx.voice_client

    await ctx.send(f"🔍 កំពុងស្វែងរកបទចម្រៀង៖ {search}...")

    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
        try:
            if search.startswith("http"):
                info = ytdl.extract_info(search, download=False)
            else:
                info = ytdl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            
            url = info['url']
            title = info['title']
        except Exception as e:
            return await ctx.send("❌ មិនអាចទាញយកបទចម្រៀងនេះបានទេ (YouTube Block IP របស់ Host)។")

    if vc.is_playing():
        vc.stop()

    # ហៅប្រើប្រាស់ប្រព័ន្ធចាក់ភ្លេងជាមួយផ្លូវ FFmpeg ថ្មី
    source = await discord.FFmpegOpusAudio.from_probe(url, executable=ffmpeg_path, **FFMPEG_OPTIONS)
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
    print("⚠️ Error: DISCORD_TOKEN variable is missing!")
