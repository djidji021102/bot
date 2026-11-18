import datetime
import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# 1. Mali web server da se bot ne bi gasio
app = Flask('')


@app.route('/')
def home():
  return 'Bot je budan i radi!'


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()


# 2. Podešavanja za bota
MOJ_ID = 1451923981601996894

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

tag_counts = {}


@bot.event
async def on_ready():
  print(f'Bot {bot.user} je uspešno pokrenut!')


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  if any(user.id == MOJ_ID for user in message.mentions):
    user_id = message.author.id
    tag_counts[user_id] = tag_counts.get(user_id, 0) + 1

    # PRVO UPOZORENJE
    if tag_counts[user_id] == 1:
      await message.channel.send(
          f'⚠️ {message.author.mention}, ovu osobu ne smeš tagovati! Još dva puta'
          ' i ide timeout na 5 minuta.'
      )
    # DRUGO UPOZORENJE
    elif tag_counts[user_id] == 2:
      await message.channel.send(
          f'⚠️ {message.author.mention}, sledeći put ide timeout!'
      )
    # TREĆI TAG -> TIMEOUT 5 MINUTA
    elif tag_counts[user_id] >= 3:
      try:
        duration = datetime.timedelta(minutes=5)
        await message.author.timeout(
            duration, reason='Ponavljano tagovanje ђинђе'
        )
        await message.channel.send(
            f'🚫 {message.author.mention} je dobio/la timeout od 5 minuta zbog'
            ' ponovljenog tagovanja.'
        )
        tag_counts[user_id] = 0
      except Exception as e:
        await message.channel.send(
            'Ne mogu primeniti timeout na ovog korisnika (proveri uloge bota'
            ' na serveru).'
        )

  await bot.process_commands(message)


# 3. Pokretanje (uzima token bezbedno)
if __name__ == '__main__':
  keep_alive()
  TOKEN = os.getenv('DISCORD_TOKEN')
  bot.run(TOKEN)
