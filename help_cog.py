#importing discord library

import discord
from discord.ext import commands 

class help_cog(commands.Cog): #defines a help class 
    def __init__(self,bot):
        self.bot = bot #creates a bot instance
        
        #personalized help message
        self.help_message = """ 
        ```
        Commands:
        
        /help - Displays all available commands
        /p <keyword> - Plays the song 
        /q - Displays the queue
        /skip - Skips the song
        /clear - Clears the queue
        /leave - Disconnect Bot
        /pause - Pause
        /resume - Resume
        ```
        """
        self.text_channels = [] #list to store text channels

    @commands.Cog.listener() #event listener
    async def on_ready(self):  #runs the bot when it is ready
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channels.append(channel) 

        await self.send_to_all(self.help_message) #sends the help message in all channels

    async def send_to_all(self, msg): #asynchronus func to send to help msg to all channels
        for text_channel in self.text_channels:
            await text_channel.send(msg)

    @commands.command(name="help",help="Displays all available functions") #a new command help defined
    async def help(self,ctx):
        await ctx.send(self.help_message)
