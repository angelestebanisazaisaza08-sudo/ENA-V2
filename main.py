import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# Configuración con el nombre de modelo más compatible
TOKEN = os.getenv('DISCORD_TOKEN')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Probamos con 'gemini-1.5-flash' o 'gemini-1.5-flash-latest'
model = genai.GenerativeModel('gemini-1.5-flash-latest')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'SISTEMA REPARADO: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                clean_text = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
                
                # Instrucción directa
                response = model.generate_content(f"Actúa como ENA, una IA sarcástica y humana. Responde a: {clean_text}")
                
                await message.reply(response.text)

            except Exception as e:
                print(f"Error detectado: {e}")
                # Si el 1.5 falla, el bot te avisará aquí
                await message.reply(f"Sigo con problemas de conexión (Error: {e}). Revisa si la API Key es de Google AI Studio.")

# Keep-alive para Render
app = Flask('')
@app.route('/')
def home(): return "ENA Online"

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(TOKEN)
                                                       
