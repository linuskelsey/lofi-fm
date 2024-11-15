import discord
from discord.ext import commands, tasks
import youtube_dl
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
VC_ID = os.getenv("VC_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# YouTube-DL options for streaming audio
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
}
ffmpeg_options = {
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Function to get a YouTube audio stream
def get_ytdl_source(url: str):
    info = ytdl.extract_info(url, download=False)
    return info['url']

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Check if the specific VC is occupied
    if after.channel and after.channel.id == VC_ID:
        vc = discord.utils.get(member.guild.voice_channels, id=VC_ID)
        if len(vc.members) > 0 and not any(b.voice_client for b in bot.voice_clients):
            # Join the VC and start playing lo-fi music
            await join_and_play(vc)

async def join_and_play(vc):
    try:
        vc_client = await vc.connect()
        lo_fi_url = "https://www.youtube.com/watch?v=0kkDatuTzqE"  # Replace with your desired lo-fi stream
        audio_source = get_ytdl_source(lo_fi_url)
        vc_client.play(discord.FFmpegPCMAudio(audio_source, **ffmpeg_options))

        # Stay in the VC until it becomes empty
        while len(vc.members) > 1:  # Adjust logic if bot counts as a member
            await asyncio.sleep(5)

        await vc_client.disconnect()
    except Exception as e:
        print(f"Error: {e}")
        if vc_client:
            await vc_client.disconnect()

@bot.command()
async def stop(ctx):
    # Disconnect the bot from VC if requested
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")

bot.run(DISCORD_TOKEN)