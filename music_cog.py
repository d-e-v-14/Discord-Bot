import discord 
from discord.ext import commands
from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        
        self.is_playing=False
        self.is_paused=False
        
        self.music_queue=[]
        self.YDL_OPTIONS={'format':'bestaudio','noplaylist':'True'}
        self.FFMPEG_OPTIONS={'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay max 5','options':'-vn'}
        self.vc=None
        
    def search_yt(self,item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info=ydl.extract_info("ytsearch%s"%item,download=False)['entries'][0]
            except Exception:
                return False
        return {'source': info['formats'][0]['url'], 'title':info['title']}
    
    def play_next(self):
        if len(self.music_queue)>0:
            self.is_playing=True
            m_url=self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url,**self.FFMPEG_OPTIONS),after=lambda e:self.play_next())
        else:
            self.is_playing=False
            
    async def play_music(self,ctx):
        if len(self.music_queue)>0:
            self.is_playing=True
            m_url=self.music_queue[0][0]['source']
            
            if self.vc==None or not self.vc.is_connected():
                self.vc=await self.music_queue[0][1].connect()
                
                if self.vc==None:
                    await ctx.send("Could not connect to the voce channel")
                    return 
                else:
                    await self.vc.move_to(self.music_queue[0][1])
                    
                self.music_queue.pop(0)
                
                self.vc.play(discord.FFmpegAudio(m_url,**self.FFMPEG_OPTIONS),after=lambda e:self.play_next())
            else:
                self.is_playing=False
    @commands.command(name="play", aliases=["p", "playing"], help="Play the selected song")
    async def play(self, ctx, *args):
        query = " ".join(args)


        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
            return
        if self.vc is None or not self.vc.is_connected():
            self.vc = await self.music_queue[0][1].connect()
            
        if self.is_paused:
            await self.vc.resume()
        else:
            song = self.search_yt(query)
            if isinstance(song, bool):  
                await ctx.send("Could not download, try again")
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing: 
                    await self.play_music(ctx)
                            
    @commands.command(name="pause",help="Pause the current song being played")
    async def pause(self,ctx,*args):
        if self.is_playing:
            self.is_playing=False
            self.is_paused=True
            self.vc.pause()
        elif self.is_paused:
            self.vc.resume()
                    
    @commands.command(name="resume",help="Resume the current song")
    async def resume(self,ctx,*args):
        if self.is_paused:
            self.is_playing=True
            self.is_paused=False
            self.vc.resume()
            
    @commands.command(name="skip",help="Skips the song currently being played")
    async def skip(self,ctx,*args):
        if self.vc is not None:
            self.vc.stop()
            await self.play_music(ctx)
            
    @commands.command(name="queue",aliases=["q"],help="Displays all the songs currently in queue")
    async def queue(self,ctx):
        retval=""
        
        for i in range(0,len(self.music_queue)):
            if i>4: break
            retval+=self.music_queue[i][0]['title']+'\n'
            
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music is in the queue")
            
    @commands.command(name="clear",aliases=["c","bin"],help="Stops the current song and clears the queue")
    async def clear(self,ctx,*args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")
    @commands.command(name="leave",aliases=["disconnect","l","d"],help="kick the bot from voice channel")
    async def leave(self,ctx):
        self.is_playing=False
        self.is_paused=False
        await self.vc.disconnect()
    
