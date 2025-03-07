#imports libraries
import discord 
import asyncio
from discord.ext import commands
from yt_dlp import YoutubeDL 

class music_cog(commands.Cog): #music cog class created
    def __init__(self, bot):
        self.bot=bot #bot instance initialized

        self.is_playing=False #tracks if the bot is playing or paused
        self.is_paused=False

        self.music_queue=[] #empty list for quoes created
        self.YDL_OPTIONS={'format':'bestaudio/best', 'noplaylist': 'True'} #ensures best audio quality
        self.FFMPEG_OPTIONS={'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=3.0"'}
        self.vc=None #stores the bots voice connection

    def search_yt(self, item): #function to search
        with YoutubeDL(self.YDL_OPTIONS) as ydl:  #youtubeDL library utilized
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False) #searches for audio without downloading
                if 'entries' in info and len(info['entries']) > 0: #if audio is found, downloads the audio file
                    best_audio = next(
                            (format for format in info['entries'][0]['formats']
                             if format.get('acodec') and format['acodec'] != 'none'), #specifies the audio format
                             None)
                    if best_audio:
                        return {'source': best_audio['url'], 'title': info['entries'][0]['title']} #returns the title of audio
                return False
            except Exception as e:
                print(f"Error extracting audio: {e}") #prints error if some error is encountered during playing audio
                return False

    def play_next(self): #skipping the queue command
        if len(self.music_queue) > 0: #checks the queue length
            self.is_playing = True #checks if bot is playing
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0) 
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 
                         after=lambda _: self.bot.loop.create_task(self.play_music()))  #automatically plays the next song
        else:
            self.is_playing=False #if queue is empty then stops playing

    async def play_music(self, ctx=None): #function to play music
        if len(self.music_queue) > 0:
            self.is_playing=True
            m_url = self.music_queue[0][0]['source'] #retrieves the songs URL
            voice_channel = self.music_queue[0][1]

            if self.vc is None or not self.vc.is_connected():  #joins the vc if not connected
                self.vc = await voice_channel.connect()
                print(f"Connected to {voice_channel}")
            elif self.vc.channel != voice_channel: #jumping voice channels
                await self.vc.move_to(voice_channel)
                print(f"Moved to {voice_channel}")

            if self.vc is None:
                if ctx:
                    await ctx.send("Could not connect to the voice channel") #returns error if vc denies connection
                return

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 
                         after=lambda _: self.bot.loop.create_task(self.play_next())) #bots voice client plays the song by interacting using ffmpeg 
    #play command defination
    @commands.command(name="play", aliases=["p", "playing"], help="Play the selected song")
    async def play(self, ctx, *args): #accepts arguments for checking if the user is following correct steps
        query = " ".join(args) #accepts all additional commands after calling command

        voice_channel = ctx.author.voice.channel if ctx.author.voice else None #checks if user is connected to a vc
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
            return
        
        if self.is_paused:
            self.vc.resume()#resumes the music if it is paused
        else: #adds the song to the queue if not alrdy added
            song = self.search_yt(query)
            if isinstance(song, bool):  
                await ctx.send("Could not download, try again")
            else:
                await ctx.send(f"Added to queue: **{song['title']}**")
                self.music_queue.append([song, voice_channel]) #appends song to channel
                
                if not self.is_playing:
                    await self.play_music(ctx) #if music is not playing, it plays it

    @commands.command(name="pause", help="Pause the current song being played")
    async def pause(self, ctx, *args):
        if self.vc is not None and self.is_playing:  
            self.is_playing=False
            self.is_paused=True
            self.vc.pause()
    #pause command definition
    @commands.command(name="resume", help="Resume the current song")
    async def resume(self,ctx,*args): #asynchronus function defined for pausing 
        if self.vc is not None and self.is_paused:
            self.is_playing=True
            self.is_paused=False
            self.vc.resume()
    #command to skip 
    @commands.command(name="skip", help="Skips the song currently being played")
    async def skip(self, ctx, *args):
        if self.vc is not None and self.vc.is_playing():  
            self.vc.stop()
            await self.play_music(ctx)
            
    #leave command for exiting the bot
    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from voice channel")
    async def leave(self, ctx):
        if self.vc is not None:  
            await self.vc.disconnect() #disconnects bot from vc
            self.vc = None
        self.is_playing = False
        self.is_paused = False
