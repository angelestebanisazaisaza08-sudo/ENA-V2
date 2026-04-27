import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- 1. CONFIGURACIÓN DE NÚCLEO ---
TOKEN = os.getenv('DISCORD_TOKEN')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configuración de comportamiento (Aquí vive la esencia de ENA)
SYSTEM_INSTRUCTION = (
    "Eres ENA, una IA con una personalidad humana, sarcástica, ingeniosa y un poco impredecible. "
    "No actúes como un asistente aburrido. Usa un lenguaje natural y directo."
)

# Inicialización del modelo con la instrucción de sistema
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

# --- 2. LÓGICA DE RESPUESTA ---
async def generar_respuesta_ena(texto_usuario):
    try:
        # Generamos contenido con un límite de tokens para que sea rápida
        response = model.generate_content(
            texto_usuario,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.8, # Un poco de "locura" controlada
            )
        )
        
        # Verificamos si hay texto (a veces Gemini bloquea por seguridad)
        if response.parts:
            return response.text
        else:
            return "Mi cerebro acaba de censurar esa respuesta. Intenta preguntar algo menos... 'peligroso'."
            
    except Exception as e:
        print(f"DEBUG LOG: {e}")
        return f"Tuve un calambre cerebral técnico. Error: {str(e)[:50]}"

# --- 3. EVENTOS DE DISCORD ---
@client.event
async def on_ready():
    # Cambia el estado del bot para que se vea profesional
    await client.change_presence(activity=discord.Game(name="Analizando humanos"))
    print(f'>>> ENA V2.0 ONLINE: {client.user}')

@client.event
async def on_message(message):
    # Ignorar mensajes de bots (incluida ella misma)
    if message.author.bot:
        return

    # Responder solo si la mencionan o es mensaje privado
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            # Limpiar menciones del texto para no confundir a la IA
            clean_text = message.content
            for mention in message.mentions:
                clean_text = clean_text.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
            clean_text = clean_text.strip()

            if not clean_text:
                await message.reply("¿Me mencionas pero no dices nada? Qué humano de tu parte.")
                return

            respuesta = await generar_respuesta_ena(clean_text)
            
            # Asegurar que no exceda el límite de Discord (2000 carac.)
            if len(respuesta) > 2000:
                await message.reply(respuesta[:1950] + "...")
            else:
                await message.reply(respuesta)

# --- 4. SUPERVIVENCIA (FLASK) ---
app = Flask('')
@app.route('/')
def home(): return "ENA Status: Operacional"

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(TOKEN)
      
