import os

import discord

from typing import Final

from dotenv import load_dotenv

from logs_system import LogsSystem


load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

logs_system = LogsSystem(client)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return None

    await logs_system.write_to_logs(message)


@client.event
async def on_message_delete(message: discord.Message) -> None:
    if message.author == client.user:
        return None

    await logs_system.delete_to_logs(message)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message) -> None:
    if before.author == client.user:
        return None

    await logs_system.edit_to_logs(before, after)

client.run(TOKEN)
