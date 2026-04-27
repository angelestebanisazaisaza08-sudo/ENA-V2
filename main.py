import discord
import os
import google.generativeai as genai
import random
import time
from flask import Flask
from threading import Thread
from duckduckgo_search import DDGS
from gestor_memoria import cargar_memoria, guardar_memoria, obtener_contexto_usuario

# --- CONFIGURACIÓN IA ---
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

# --- LÓGICA DE PERSONALIDAD ---
class PersonalidadENA:
    def __init__(self):
        self.actual = "ALTA"
        self.ultima_actualizacion = time.time()
        self.duracion_minima = 1800 

    def obtener_contexto(self):
        ahora = time.time()
        if ahora - self.ultima_actualizacion > self.duracion_minima:
            if random.random() > 0.5:
                self.actual = "ALTA" if self.actual == "RETRAIDA" else "RETRAIDA"
                self.ultima_actualizacion = ahora
        
        if self.actual == "ALTA":
            return "Personalidad: Autoestima alta, superioridad, brillante y arrogante."
        return "Personalidad: Retraída, insegura, desconfiada y tímida."

ena_estado = PersonalidadENA()

def investigar(query):
    try:
        with DDGS() as ddgs:
            resultados = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(resultados)
    except: return "Búsqueda fallida."

# --- DISCORD ---
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author.bot: return

    content = message.content.lower()
    es_ena = "ena" in content or client.user.mentioned_in(message)
    es_dm = isinstance(message.channel, discord.DMChannel)

    if es_ena or es_dm:
        async with message.channel.typing():
            try:
                # 1. Recuperar Memoria y Contexto
                memoria_usuario = obtener_contexto_usuario(message.author.id)
                contexto_personalidad = ena_estado.obtener_contexto()
                
                # 2. Investigación (si aplica)
                info_web = ""
                if any(x in content for x in ["investiga", "busca", "quién es"]):
                    info_web = f"\n[INVESTIGACIÓN WEB]: {investigar(message.content)}"

                # 3. Prompt Maestro
                prompt = (
                    f"Tu contexto de personalidad: {contexto_personalidad}\n"
                    f"Usuario actual: {message.author.display_name}\n"
                    f"{memoria_usuario}\n"
                    f"{info_web}\n"
                    f"Mensaje nuevo: {message.content}\n"
                    f"Responde usando tu memoria y personalidad. Sé breve."
                )

                response = model.generate_content(prompt)
                
                if response.text:
                    # 4. GUARDAR EN MEMORIA
                    guardar_memoria(message.author.id, message.author.name, message.content, response.text)
                    await message.reply(response.text)
            
            except Exception as e:
                print(f"Error: {e}")
                await message.reply("Mi memoria tuvo un glitch... ¿qué decíamos?")

# --- SERVER KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "ENA PRO + MEMORY: ONLINE", 200

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    client.run(os.getenv('DISCORD_TOKEN'))
      
