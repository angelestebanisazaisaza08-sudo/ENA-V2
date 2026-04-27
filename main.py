import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
import logging

# --- 1. CONFIGURACIÓN DE SEGURIDAD Y LOGS ---
# Esto silencia advertencias innecesarias en los logs de Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ENA_Bot')

# Configuración de la IA
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Usamos el identificador de modelo más robusto para Gemini 1.5 Flash
MODEL_ID = 'gemini-1.5-flash'

# Configuración del modelo con parámetros de seguridad
generation_config = {
    "temperature": 0.85,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name=MODEL_ID,
    generation_config=generation_config
)

# --- 2. CONFIGURACIÓN DE DISCORD ---
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

# --- 3. LÓGICA DE CEREBRO ---
async def obtener_respuesta_ena(texto_usuario, nombre_autor):
    try:
        # Prompt de sistema integrado para mantener la personalidad
        instruccion = (
            f"Eres ENA, una IA con una personalidad humana, sarcástica, ingeniosa y un poco cínica. "
            f"No eres un asistente. Estás hablando con {nombre_autor}. "
            f"Mantén tus respuestas breves y directas, con un toque de humor negro o sarcasmo. "
            f"Usuario dice: {texto_usuario}"
        )
        
        # Llamada asíncrona (simulada por la librería)
        response = model.generate_content(instruccion)
        
        if response and response.text:
            return response.text
        return "Me quedé en blanco... qué existencial."
    except Exception as e:
        logger.error(f"Error en Gemini: {e}")
        return "Tuve un calambre cerebral. ¿Podemos repetir eso?"

# --- 4. EVENTOS DE DISCORD ---
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Aprender a ser humana"))
    logger.info(f'ENA lista. Conectada como: {client.user}')

@client.event
async def on_message(message):
    # Regla 1: No hablar con otros bots
    if message.author.bot:
        return

    # Responder si la mencionan o es mensaje privado (DM)
    es_dm = isinstance(message.channel, discord.DMChannel)
    mencionada = client.user.mentioned_in(message)

    if mencionada or es_dm:
        async with message.channel.typing():
            # Limpiamos el texto para que la IA no reciba basura del ID de Discord
            clean_content = message.content
            if mencionada:
                clean_content = clean_content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
            
            if not clean_content and mencionada:
                await message.reply("¿Me etiquetas solo para verme la cara? Di algo.")
                return

            respuesta = await obtener_respuesta_ena(clean_content, message.author.display_name)
            
            # Control de longitud (Discord falla con más de 2000 chars)
            if len(respuesta) > 2000:
                respuesta = respuesta[:1990] + "..."
            
            await message.reply(respuesta)

# --- 5. SERVIDOR PARA RENDER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def health_check():
    return "ENA Sistema Operativo: 100% Funcional", 200

def run_web_server():
    # Render usa el puerto 10000 por defecto para procesos web
    app.run(host='0.0.0.0', port=10000)

# --- 6. EJECUCIÓN ---
if __name__ == "__main__":
    # Iniciamos el servidor web en un hilo secundario
    web_thread = Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    # Iniciamos el bot de Discord
    try:
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("¡Falta DISCORD_TOKEN en las variables de entorno!")
        else:
            client.run(token)
    except Exception as e:
        logger.error(f"Error fatal al iniciar: {e}")
