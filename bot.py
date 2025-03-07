#imports the modules
import discord
import os
import asyncio
from discord.ext import commands

from help_cog import help_cog
from music_cog import music_cog

from google import genai
from google.genai.types import Content, GenerateContentConfig

from dotenv import load_dotenv

load_dotenv() #loads the keys

intents = discord.Intents.default() #enables default bot perms
intents.message_content=True #allows bot to read messages
bot = commands.Bot(command_prefix="/", intents=intents) #sets prefix as /
bot.remove_command("help")  #removes default help

BOT_TOKEN = os.getenv("BOT_TOKEN")

MAX=2000

#function to split the long text msgs given by gemini(word limit in discord)
def split_message(text, max_length=MAX):
    return [text[i:i+max_length] for i in range(0, len(text),max_length)]

#function to integrate gemini
def generate(text):
    client=genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    ) #creates a gen.ai object for interacting with gemini AI

    model="gemini-2.0-flash"
    contents=[
        Content(
            role="user",
            parts=[{"text":text}], #passes the text to gemini
        ),
    ]
    generate_content_config=GenerateContentConfig(
        temperature=1.55, #creativity factor
        top_p=0.95, #sampling randomness
        top_k=40, #limits number of responses
        max_output_tokens=8192, #max length limit
        response_mime_type="text/plain",
    )
    response_text = ""
    
    #function to generate responses
    for chunk in client.models.generate_content_stream( 
        model=model, #uses the mentioned model
        contents=contents, #refers to contents mentioned above
        config=generate_content_config, #refers to configured settings above
    ):
        if chunk.text:
            response_text += chunk.text #concatenates response into response string
    return response_text if response_text else "I couldn't generate a response"

@bot.event #calls the bot even, bot performs this event
async def on_ready():
    print(f'We have logged in as {bot.user}') #displays msg in terminal as soon as bot logs in

@bot.event #prevents bot from responding to itself
async def on_message(message):
    if message.author==bot.user:
        return

    if message.content.startswith('$'): #passes only those msgs to gemini which start with $
       user_input=message.content[1:]  #reads the user input
       response=generate(user_input)  #generates the response by passing it to gemini api
       parts=split_message(response)  #spilts the response due to discord maximum limit
       for part in parts:
            await message.channel.send(part) #sends msg in multiple parts

    await bot.process_commands(message) #allows normal commands to work

@bot.command()
async def ping(ctx):
    await ctx.send(".") #responds with . when user inputs /ping

async def load_cogs():
    await bot.add_cog(help_cog(bot)) #loads help cog
    await bot.add_cog(music_cog(bot)) #loads music og

async def main(): #waits for the task to be called
    async with bot:
        await load_cogs() #awaits the response from load cogs function
        await bot.start(BOT_TOKEN) #loads the token key

asyncio.run(main()) #runs the main by calling it inside and async event loop
