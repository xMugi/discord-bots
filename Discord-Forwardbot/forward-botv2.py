import discord
import asyncio
import json
import os
from collections import deque

# --- KONFIGURATION LADEN ---
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    USER_TOKEN = config.get("user_token")
    WEBHOOK_URL = config.get("destination_webhook_url")
    SOURCE_CHANNEL_IDS = config.get("source_channel_ids", [])
except FileNotFoundError:
    print("Fehler: Die Datei 'config.json' wurde nicht gefunden. Bitte erstelle sie.")
    exit()
except json.JSONDecodeError:
    print("Fehler: Die Datei 'config.json' ist fehlerhaft formatiert.")
    exit()

# --- EINSTELLUNGEN ---
# Wie viele Nachrichten pro Kanal im Nachhol-Modus abgerufen werden sollen.
CATCH_UP_MESSAGE_LIMIT = 8

# Wie viele Nachrichten-IDs maximal in der Log-Datei gespeichert werden sollen.
# Sollte größer oder gleich CATCH_UP_MESSAGE_LIMIT * Anzahl_Kanäle sein.
LOG_ID_LIMIT = CATCH_UP_MESSAGE_LIMIT * len(SOURCE_CHANNEL_IDS)

# Wie viele Sekunden zwischen dem Senden jeder Nachricht gewartet werden soll
MESSAGE_DELAY_SECONDS = 3

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
        source_channel_info = f"#{message.channel.name} ({message.guild.name})"
        webhook_username_info = f"in #{message.channel.name}"
    else:
        source_channel_info = "Direktnachricht"
        webhook_username_info = "in einer Direktnachricht"

    safe_content = message.content.replace('@everyone', '@ everyone').replace('@here', '@ here')

    print(f'Sende Nachricht von {message.author.name} in {source_channel_info} weiter...')
    
    try:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, client=client)
        await webhook.send(
            content=safe_content,
            username=f"{message.author.name} | {webhook_username_info}",
            avatar_url=message.author.avatar.url if message.author.avatar else None,
            embeds=message.embeds,
            files=[await f.to_file() for f in message.attachments]
        )
        print("Nachricht erfolgreich weitergeleitet.")

        sent_message_ids.append(message.id)
        with open(SENT_MESSAGES_LOG, 'w', encoding='utf-8') as f:
            for msg_id in sent_message_ids:
                f.write(str(msg_id) + '\n')
    except Exception as e:
        print(f"Fehler beim Senden des Webhooks: {e}")

async def catch_up():
    """Holt die letzten Nachrichten aus den Kanälen nach, die noch nicht gesendet wurden."""
    print("Starte den Nachhol-Modus...")
    missed_messages = []
    
    for channel_id in SOURCE_CHANNEL_IDS:
        try:
            channel = await client.fetch_channel(channel_id)
            print(f'Überprüfe Kanal {channel.name} auf verpasste Nachrichten...')
            async for message in channel.history(limit=CATCH_UP_MESSAGE_LIMIT):
                if message.id not in sent_message_ids and message.author != client.user:
                    missed_messages.append(message)
        except Exception as e:
            print(f"Fehler beim Nachholen von Nachrichten im Kanal {channel_id}: {e}")
            
    missed_messages.sort(key=lambda msg: msg.id)
    print(f'Gefundene {len(missed_messages)} verpasste Nachrichten zum Nachholen.')

    for message in missed_messages:
        await send_webhook_message(message)
        await asyncio.sleep(MESSAGE_DELAY_SECONDS)
        
    print("Nachhol-Modus abgeschlossen.")

@client.event
async def on_ready():
    print(f'Erfolgreich eingeloggt als: {client.user}')
    print(f'Überwache {len(SOURCE_CHANNEL_IDS)} Kanäle.')
    print(f'Geladene IDs aus dem Log: {len(sent_message_ids)}')
    print(f'Leite Nachrichten an den konfigurierten Webhook weiter.')

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
        print("Fehler: Bitte stelle sicher, dass 'config.json' die Werte für 'user_token', 'destination_webhook_url' und 'source_channel_ids' enthält.")
        return
    await client.start(USER_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot wird beendet.")