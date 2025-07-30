import discord
import asyncio
import json
import os
from collections import deque
import logging

# --- LOGGING-KONFIGURATION ---
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- KONFIGURATION LADEN ---
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    USER_TOKEN = config.get("user_token")
    WEBHOOK_URL = config.get("destination_webhook_url")
    SOURCE_CHANNEL_IDS = config.get("source_channel_ids", [])
    BOT_DISPLAY_NAME = config.get("bot_display_name", "Webhook-Bot")
    BOT_AVATAR_URL = config.get("bot_avatar_url")
    
except FileNotFoundError:
    logging.error("Fehler: Die Datei 'config.json' wurde nicht gefunden. Bitte erstelle sie.")
    exit()
except json.JSONDecodeError:
    logging.error("Fehler: Die Datei 'config.json' ist fehlerhaft formatiert.")
    exit()

# --- EINSTELLUNGEN ---
CATCH_UP_MESSAGE_LIMIT = 5
LOG_ID_LIMIT = CATCH_UP_MESSAGE_LIMIT * len(SOURCE_CHANNEL_IDS) + 30
MESSAGE_DELAY_SECONDS = 2

# --- LOG-DATEI LADEN UND BEGRENZEN ---
SENT_MESSAGES_LOG = 'sent_messages.log'
sent_message_ids = deque(maxlen=LOG_ID_LIMIT) 

if os.path.exists(SENT_MESSAGES_LOG):
    with open(SENT_MESSAGES_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            sent_message_ids.append(int(line.strip()))

# Initialisiere den Client
client = discord.Client()

async def send_webhook_message(message: discord.Message):
    """Eine Hilfsfunktion, um den Webhook zu senden."""
    if message.guild:
        source_channel_info = f"in #{message.channel.name}"
    else:
        source_channel_info = "in einer Direktnachricht"

    safe_content = message.content.replace('@everyone', '@ everyone').replace('@here', '@ here')

    logging.info(f'Sende Nachricht von {BOT_DISPLAY_NAME} | {source_channel_info} weiter...')
    
    try:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, client=client)
        await webhook.send(
            content=f"{safe_content}\n\n",
            username=f"{BOT_DISPLAY_NAME} | {source_channel_info}",
            avatar_url=BOT_AVATAR_URL,
            embeds=message.embeds,
            files=[await f.to_file() for f in message.attachments]
        )
        logging.info("Nachricht erfolgreich weitergeleitet.")

        sent_message_ids.append(message.id)
        with open(SENT_MESSAGES_LOG, 'w', encoding='utf-8') as f:
            for msg_id in sent_message_ids:
                f.write(str(msg_id) + '\n')
    except Exception as e:
        logging.error(f"Fehler beim Senden des Webhooks: {e}")

async def catch_up():
    """Holt die letzten Nachrichten aus den Kanälen nach, die noch nicht gesendet wurden."""
    logging.info("Starte den Nachhol-Modus...")
    missed_messages = []
    
    for channel_id in SOURCE_CHANNEL_IDS:
        try:
            channel = await client.fetch_channel(channel_id)
            logging.info(f'Überprüfe Kanal {channel.name} auf verpasste Nachrichten...')
            async for message in channel.history(limit=CATCH_UP_MESSAGE_LIMIT):
                if message.id not in sent_message_ids and message.author != client.user:
                    missed_messages.append(message)
        except Exception as e:
            logging.error(f"Fehler beim Nachholen von Nachrichten im Kanal {channel_id}: {e}")
            
    missed_messages.sort(key=lambda msg: msg.id)
    logging.info(f'Gefundene {len(missed_messages)} verpasste Nachrichten zum Nachholen.')

    for message in missed_messages:
        await send_webhook_message(message)
        await asyncio.sleep(MESSAGE_DELAY_SECONDS)
        
    logging.info("Nachhol-Modus abgeschlossen.")

@client.event
async def on_ready():
    logging.info(f'Erfolgreich eingeloggt als: {client.user}')
    logging.info(f'Überwache {len(SOURCE_CHANNEL_IDS)} Kanäle.')
    logging.info(f'Geladene IDs aus dem Log: {len(sent_message_ids)}')
    logging.info(f'Leite Nachrichten an den konfigurierten Webhook weiter.')

    await catch_up()

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or message.id in sent_message_ids:
        return

    if message.channel.id in SOURCE_CHANNEL_IDS:
        await send_webhook_message(message)
        await asyncio.sleep(MESSAGE_DELAY_SECONDS)

async def main():
    if not all([USER_TOKEN, WEBHOOK_URL, SOURCE_CHANNEL_IDS]):
        logging.error("Fehler: Bitte stelle sicher, dass 'config.json' die Werte für 'user_token', 'destination_webhook_url' und 'source_channel_ids' enthält.")
        return
    await client.start(USER_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot wird beendet.")
