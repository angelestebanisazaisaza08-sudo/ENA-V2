import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# Configuración básica
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'ENA lista y conectada como {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # Limpiar el texto
                user_input = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
                
                # Prompt directo
                prompt = f"Eres ENA, una IA sarcástica y humana. Responde brevemente a: {user_input}"
                
                response = model.generate_content(prompt)
                
                if response and response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Me quedé sin palabras... intenta de nuevo.")

            except Exception as e:
                # Esto nos dirá el error exacto en Discord si algo falla
                await message.reply(f"Error de conexión con el cerebro: {str(e)[:100]}")

# Servidor para Render
app = Flask('')
@app.route('/')
def home(): return "ENA Online", 200

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    client.run(os.getenv('DISCORD_TOKEN'))
      
