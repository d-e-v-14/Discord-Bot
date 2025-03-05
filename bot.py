import discord
import os
import asyncio
from discord.ext import commands
from help_cog import help_cog
from music_cog import music_cog
from google import genai
from google.genai.types import Content, GenerateContentConfig
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

BOT_TOKEN = os.getenv("BOT_TOKEN")

MAX_MESSAGE_LENGTH = 2000

client = commands.Bot(command_prefix="/", intents=intents)
client.remove_command("help") 

def split_message(text, max_length=MAX_MESSAGE_LENGTH):
    return [text[i:i+max_length] for i in range(0,len(text),max_length)]

def generate(text):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        Content(
            role="user",
            parts=[{"text": text}], 
        ),
    ]
    generate_content_config = GenerateContentConfig(
        temperature=1.55,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        
        if chunk.text:
            response_text += chunk.text
    return response_text if response_text else "I couldn't generate a response"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
       user_input = message.content[1:]  
       response = generate(user_input)  
       parts = split_message(response)  
       for part in parts:
            await message.channel.send(part)

async def load_cogs():
    await client.add_cog(help_cog(client))
    await client.add_cog(music_cog(client))


async def main():
    async with client:
        await load_cogs()
        await client.start(BOT_TOKEN)

asyncio.run(main())
