import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN = os.getenv('DISCORD_TOKEN')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Configuración del modelo más directa
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# --- EVENTOS ---
@client.event
async def on_ready():
    print(f'ENA ONLINE y lista para el caos.')

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # Limpiamos el texto de la mención para que Gemini no se confunda
                texto_usuario = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
                
                prompt_final = f"Eres ENA, una IA con personalidad humana, sarcástica y algo impredecible. Responde a esto: {texto_usuario}"
                
                # Generación directa
                response = model.generate_content(prompt_final)
                
                # Si Gemini responde vacío o bloquea, usamos un plan B
                texto_respuesta = response.text if response.text else "Me quedé pensando en la nada... repite eso."
                
                if len(texto_respuesta) > 2000:
                    texto_respuesta = texto_respuesta[:1950] + "..."
                
                await message.reply(texto_respuesta)

            except Exception as e:
                # Esto imprimirá el error REAL en los logs de Render
                print(f"DEBUG ERROR: {e}")
                await message.reply(f"Hubo un error técnico real: {e}")

# --- MANTENER VIVA ---
app = Flask('')
@app.route('/')
def home(): return "ENA Status: OK"

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(TOKEN)
                                                       
