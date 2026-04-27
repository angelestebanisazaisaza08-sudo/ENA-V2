import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# Configuración forzando la versión estable de la API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configuramos el modelo de forma que no busque rutas inexistentes
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'ENA ONLINE Y ESTABLE')

@client.event
async def on_message(message):
    if message.author.bot: return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                user_input = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
                
                # Enviar mensaje directo al modelo
                response = model.generate_content(f"Eres ENA, una IA sarcástica. Responde a: {user_input}")
                
                if response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Cerebro vacío. Intenta otra vez.")

            except Exception as e:
                # Si esto sale, el error 404 ha muerto y sabremos la causa real
                await message.reply(f"Ajuste técnico final: {str(e)[:100]}")

app = Flask('')
@app.route('/')
def home(): return "ENA Live", 200

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    client.run(os.getenv('DISCORD_TOKEN'))
  
