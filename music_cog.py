import discord 
import asyncio
from discord.ext import commands
from yt_dlp import YoutubeDL 

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

        self.is_playing=False
        self.is_paused=False

        self.music_queue=[]
        self.YDL_OPTIONS={'format':'bestaudio/best', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS={'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=3.0"'}
        self.vc=None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:  
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    best_audio = next(
                            (format for format in info['entries'][0]['formats']
                             if format.get('acodec') and format['acodec'] != 'none'), 
                             None)
                    if best_audio:
                        return {'source': best_audio['url'], 'title': info['entries'][0]['title']}
                return False
            except Exception as e:
                print(f"Error extracting audio: {e}")
                return False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 
                         after=lambda _: self.bot.loop.create_task(self.play_music()))  
        else:
            self.is_playing=False

    async def play_music(self, ctx=None):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            voice_channel = self.music_queue[0][1]

            if self.vc is None or not self.vc.is_connected(): 
                self.vc = await voice_channel.connect()
                print(f"Connected to {voice_channel}")
            elif self.vc.channel != voice_channel:
                await self.vc.move_to(voice_channel)
                print(f"Moved to {voice_channel}")

            if self.vc is None:
                if ctx:
                    await ctx.send("Could not connect to the voice channel")
                return

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 
                         after=lambda _: self.bot.loop.create_task(self.play_next()))  

    @commands.command(name="play", aliases=["p", "playing"], help="Play the selected song")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
            return
        
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if isinstance(song, bool):  
                await ctx.send("Could not download, try again")
            else:
                await ctx.send(f"Added to queue: **{song['title']}**")
                self.music_queue.append([song, voice_channel])
                
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pause the current song being played")
    async def pause(self, ctx, *args):
        if self.vc is not None and self.is_playing:  
            self.is_playing=False
            self.is_paused=True
            self.vc.pause()

    @commands.command(name="resume", help="Resume the current song")
    async def resume(self,ctx,*args):
        if self.vc is not None and self.is_paused:
            self.is_playing=True
            self.is_paused=False
            self.vc.resume()

    @commands.command(name="skip", help="Skips the song currently being played")
    async def skip(self, ctx, *args):
        if self.vc is not None and self.vc.is_playing():  
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from voice channel")
    async def leave(self, ctx):
        if self.vc is not None:  
            await self.vc.disconnect()
            self.vc = None
        self.is_playing = False
        self.is_paused = False
