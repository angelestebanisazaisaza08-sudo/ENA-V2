import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# Config
TOKEN = os.getenv('DISCORD_TOKEN')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'SISTEMA LIMPIO: {client.user} iniciado.')

@client.event
async def on_message(message):
    if message.author == client.user: return
    if client.user.mentioned_in(message):
        res = model.generate_content(f"Eres ENA, sarcástica. Responde: {message.content}")
        await message.reply(res.text)

# Keep-alive básico
app = Flask('')
@app.route('/')
def home(): return "ENA Online"

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(TOKEN)
  
