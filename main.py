import discord, os, google.generativeai as genai
from flask import Flask
from threading import Thread

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_message(message):
    if message.author.bot or not client.user.mentioned_in(message): return
    async with message.channel.typing():
        try:
            res = model.generate_content(f"Eres ENA, sarcástica. Responde a: {message.content}")
            await message.reply(res.text)
        except Exception as e:
            await message.reply(f"Error: {e}")

app = Flask('')
@app.route('/')
def home(): return "OK"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
    client.run(os.getenv('DISCORD_TOKEN'))
  
