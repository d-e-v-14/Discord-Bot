import discord
import base64
import os
from google import genai
from google.genai.types import Content,Part,GenerateContentConfig
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
       await message.channel.send(response) 
        


client.run(BOT_TOKEN)

