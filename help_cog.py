import discord
from discord.ext import commands 

class help_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        self.help_message = """
        ```
        Commands:
        
        /help - Displays all available commands
        /p <keyword> - Plays the song in your current channel
        /q - Displays the current music queue
        /skip - Skips the currently playing song
        /clear - Stops the music and clears the queue
        /leave - Disconnects the bot from the voice channel
        /pause - Pauses or resumes the current song
        /resume - Resumes playing the current song
        ```
        """
        self.text_channels = []  # Fixed variable name

    @commands.Cog.listener()
    async def on_ready(self):  # Moved outside __init__
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channels.append(channel)  # Fixed variable reference

        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channels:
            await text_channel.send(msg)

    @commands.command(name="help",help="Displays all available functions")
    async def help(self,ctx):
        await ctx.send(self.help_message)
