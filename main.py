import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import logging
import os  # 👈 ថែមបន្ទាត់នេះចូល នៅខាងលើបង្អស់នៃកូដរបស់បង

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="T!", intents=intents)
bot.remove_command('help')

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': False,
    'skip_download': True,
    'force_generic_extractor': False,
    'ignoreerrors': True,
    # 💡 បន្ថែមលក្ខខណ្ឌទម្លុះ Bot Block របស់ YouTube ឆ្នាំ ២០២៦
    'cookiefile': None, 
    'geo_bypass': True,
    'nocheckcertificate': True
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

song_queue = {}
last_played_title = {} 
autoplay_status = {} 
room_music_style = {} 
played_history = {}  

def check_queue(ctx):
    bot.loop.create_task(check_queue_async(ctx))

async def check_queue_async(ctx):
    if ctx.guild.id in song_queue and song_queue[ctx.guild.id]:
        next_song = song_queue[ctx.guild.id].pop(0)
        await play_audio_async(ctx, next_song)
    else:
        if autoplay_status.get(ctx.guild.id, False):
            await fetch_and_play_autoplay(ctx)
        else:
            embed = discord.Embed(
                description="👋 Queue is empty. Autoplay is OFF.\nUse T!autoplay to enable infinite music!", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

def play_audio(ctx, song_data):
    bot.loop.create_task(play_audio_async(ctx, song_data))

async def play_audio_async(ctx, song_data):
    try:
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return

        last_played_title[ctx.guild.id] = song_data['title']
        
        # 💡 សម្រាប់រត់លើកុំព្យូទ័រ (Windows) ត្រូវប្រាកដថាបងមាន Folder "bin/ffmpeg/ffmpeg.exe"
        source = await discord.FFmpegOpusAudio.from_probe(
            song_data['url'], 
            executable="bin/ffmpeg/ffmpeg.exe", 
            **FFMPEG_OPTIONS
        )
        
        ctx.voice_client.play(source, after=lambda e: check_queue(ctx))
        
        embed = discord.Embed(
            description=f"🟢 Started playing: [{song_data['title']}]({song_data['url']})", 
            color=0x1ed760
        )
        if bot.user.avatar:
            embed.set_footer(text="TwT Music | Streaming Audio Source", icon_url=bot.user.avatar.url)
        else:
            embed.set_footer(text="TwT Music | Streaming Audio Source")
            
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"⚠️ Play Audio Error Detail: {e}")
        embed = discord.Embed(
            description=f"⚠️ Unplayable track detected: {song_data.get('title', 'Unknown')}\nSkipping to next song...", 
            color=0xe67e22
        )
        await ctx.send(embed=embed)
        check_queue(ctx)

async def safe_extract_info(ytdl, query):
    return await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))

async def fetch_and_play_autoplay(ctx):
    current_title = last_played_title.get(ctx.guild.id, "")
    is_remix = "remix" in current_title.lower() or "ញាក់" in current_title.lower()
    
    sweet_keywords = [
        "khmer original song suly pheng", "khmer sad song tempo tris",
        "khmer song vfx sad", "khmer sweet song lean",
        "khmer original lyric song", "khmer sad song ruthko"
    ]
    
    remix_keywords = [
        "khmer remix vando", "khmer remix 2026",
        "khmer breakmix vannda", "khmer remix fly"
    ]

    fallback_keyword = random.choice(remix_keywords) if is_remix else random.choice(sweet_keywords)

    if ctx.guild.id not in played_history:
        played_history[ctx.guild.id] = []

    if current_title and current_title not in played_history[ctx.guild.id]:
        played_history[ctx.guild.id].append(current_title)

    if len(played_history[ctx.guild.id]) > 50:
        played_history[ctx.guild.id].pop(0)

    embed = discord.Embed(description="⏭️ Autoplay: Fetching a fresh track...", color=0x2b2d31)
    await ctx.send(embed=embed)
    with yt_dlp. YoutubeDL(YTDL_OPTIONS) as ytdl:
        
     try:
            info = await safe_extract_info(ytdl, f"scsearch30:{fallback_keyword}")
            if info and 'entries' in info and info['entries']:
                valid_entries = []
                for entry in info['entries']:
                    if not entry or 'url' not in entry:
                        continue
                    title_lower = entry['title'].lower()
                    if not is_remix and ("remix" in title_lower or "breakmix" in title_lower or "club" in title_lower):
                        continue
                    is_already_played = False
                    for played_title in played_history[ctx.guild.id]:
                        if played_title.lower() in title_lower or title_lower in played_title.lower():
                            is_already_played = True
                            break
                    if not is_already_played:
                        valid_entries.append(entry)
                
                if valid_entries:
                    next_song = random.choice(valid_entries)
                else:
                    filtered_entries = [e for e in info['entries'] if e]
                    if filtered_entries:
                        next_song = random.choice(filtered_entries)
                    else:
                        next_song = None

                if next_song:
                    song_data = {'url': next_song['url'], 'title': next_song['title']}
                    await play_audio_async(ctx, song_data)
                else:
                    check_queue(ctx)
            else:
                check_queue(ctx) 
     except Exception as e:
            print(f"Autoplay Search Error: {e}")
            check_queue(ctx)

@bot.event
async def on_ready():
    print(f'=== TwT Music ONLINE ===')
    print(f'Logged in as: {bot.user.name}')
    print(f'========================')

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🎵 TwT Music - Command Guide",
        description="Here is a list of available commands to control the music bot:",
        color=0x1ed760
    )
    embed.add_field(
        name="🎤 Music Commands",
        value="• T!p [song name/link] — Play music from YouTube Link, SoundCloud Link, or Search by Name\n"
              "• T!autoplay — Toggle infinite automatic playback\n"
              "• T!skip — Skip the currently playing track",
        inline=False
    )
    embed.add_field(
        name="🚪 Management Commands",
        value="• T!stop — Stop playback, clear the queue, and leave the voice channel",
        inline=False
    )
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="TwT Music Bot • 2026 Edition", icon_url=bot.user.avatar.url)
    else:
        embed.set_footer(text="TwT Music Bot • 2026 Edition")
    await ctx.send(embed=embed)

@bot.command()
async def autoplay(ctx):
    if ctx.guild.id not in autoplay_status:
        autoplay_status[ctx.guild.id] = False
    autoplay_status[ctx.guild.id] = not autoplay_status[ctx.guild.id]
    embed = discord.Embed(
        description=f"{'🔄' if autoplay_status[ctx.guild.id] else '🛑'} **Autoplay has been turned {'ON' if autoplay_status[ctx.guild.id] else 'OFF'}!", 
        color=0x1ed760 if autoplay_status[ctx.guild.id] else 0xff0000
    )
    await ctx.send(embed=embed)

@bot.command(name="p")
async def play(ctx, *, search):
    if not ctx.author.voice:
        embed = discord.Embed(description="❌ You need to join a voice channel first!", color=0xff0000)
        return await ctx.send(embed=embed)
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect(self_deaf=True)
    
    process_msg = await ctx.send(embed=discord.Embed(description=f"🔍 Processing {search}... please wait.", color=0x2b2d31))

    # 💡 កែសម្រួល៖ បើអ្នកប្រើដាក់លីង YouTube ឱ្យវាចាក់លីងភ្លាម បើដាក់ឈ្មោះឱ្យវា Search តាម YouTube
    query = search
    if not search.startswith("http://") and not search.startswith("https://"):
        query = f"ytsearch1:{search}"

    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
        try:
            info = await safe_extract_info(ytdl, query)
            if not info:
                raise Exception("No info found")
            
            if 'entries' in info:
                if info['entries']:
                    target = info['entries'][0] # ចាប់យកបទដំបូងគេពីលទ្ធផល Search
                else:
                    raise Exception("No entries found")
            else:
                target = info
                
            song_data = {'url': target['url'], 'title': target['title']}
            
            try: await process_msg.delete()
            except: pass

        except Exception as e:
            print(f"Search Error: {e}")
            try: await process_msg.delete()
            except: pass
            embed = discord.Embed(description="❌ Could not find or play this track/link. YouTube might be blocking the request.", color=0xff0000)
            return await ctx.send(embed=embed)
        
    if ctx.guild.id not in song_queue:
        song_queue[ctx.guild.id] = []
        
    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        song_queue[ctx.guild.id].append(song_data)
        embed = discord.Embed(description=f"➕ Added to queue: **{song_data['title']}**", color=0x2b2d31)
        await ctx.send(embed=embed)
    else:
        await play_audio_async(ctx, song_data)

@bot.command()
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send(embed=discord.Embed(description="⏭️ Skipped successfully!", color=0x2b2d31))
    else:
        await ctx.send(embed=discord.Embed(description="❌ No song is currently playing.", color=0xff0000))

@bot.command()
async def stop(ctx):
    if ctx.guild.id in song_queue: song_queue[ctx.guild.id] = []
    if ctx.guild.id in last_played_title: del last_played_title[ctx.guild.id]
    if ctx.guild.id in room_music_style: del room_music_style[ctx.guild.id] 
    if ctx.guild.id in played_history: del played_history[ctx.guild.id]
    autoplay_status[ctx.guild.id] = False
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        
    await ctx.send(embed=discord.Embed(description="👋 Left the voice channel and cleared configurations.", color=0x2b2d31))

bot.run(os.getenv('DISCORD_TOKEN'))

