import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN = os.getenv('DISCORD_TOKEN')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# --- FUNCIÓN CEREBRAL ---
async def obtener_respuesta(prompt, usuario):
    try:
        # Instrucción de personalidad
        consigna = f"Eres ENA, una IA con personalidad humana y sarcástica. Hablas con {usuario}."
        full_prompt = f"{consigna}\n\nPregunta: {prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error en Gemini: {e}")
        return "Perdón, me distraje con un glitch. ¿Qué decías?"

# --- EVENTOS ---
@client.event
async def on_ready():
    print(f'###############################')
    print(f'ENA ACTIVA: {client.user}')
    print(f'###############################')

@client.event
async def on_message(message):
    # No responderse a sí misma ni a bots
    if message.author == client.user or message.author.bot:
        return

    # Responder si la mencionan o por mensaje directo
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # Muestra "Escribiendo..." en Discord
        async with message.channel.typing():
            nombre = message.author.display_name
            respuesta = await obtener_respuesta(message.content, nombre)
            
            if len(respuesta) > 2000:
                respuesta = respuesta[:1950] + "..."
            
            await message.reply(respuesta)

# --- SERVIDOR PARA RENDER ---
app = Flask('')
@app.route('/')
def home(): return "ENA está viva"

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(TOKEN)
  
