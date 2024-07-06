import discord


def add_values_to_embed(embed: discord.Embed, message: discord.Message):
    embed.add_field(name="Channel", value=f"{message.channel.jump_url}", inline=True)
    embed.add_field(name="User", value=f"{message.author.mention}", inline=True)

    embed.add_field(name="Message content", value=f"```{message.content.__repr__()}```", inline=False)
    embed.set_footer(text=f"Message id : {message.id}")


async def write_new_message_log(to_send_in: discord.Thread, message: discord.Message) -> None:
    embed = discord.Embed(
        title=f"{message.author.display_name} sent {message.jump_url}",
        color=discord.Colour.green()
    )

    add_values_to_embed(embed, message)

    await to_send_in.send(embed=embed, files=[await f.to_file() for f in message.attachments], silent=True)


async def write_deleted_message_log(to_send_in: discord.Thread, message: discord.Message) -> None:
    embed = discord.Embed(
        title=f"{message.author.display_name} deleted {message.jump_url}",
        color=discord.Colour.red()
    )

    add_values_to_embed(embed, message)

    await to_send_in.send(embed=embed, files=[await f.to_file() for f in message.attachments], silent=True)


async def write_edited_message_log(to_send_in: discord.Thread, before: discord.Message, after: discord.Message) -> None:
    embed = discord.Embed(
        title=f"{after.author.display_name} edited {after.jump_url}",
        color=discord.Colour.orange()
    )

    add_values_to_embed(embed, before)
    embed.add_field(name="New message content", value=f"```{after.content}```", inline=False)

    await to_send_in.send(embed=embed, silent=True)


class LogsSystem:
    def __init__(self, client: discord.Client):
        self.client = client

        self.logs_channel_name: str = "logs"

        self.log_channel = None

    async def write_to_logs(self, message: discord.Message) -> None:
        if str(message.channel.name) == self.logs_channel_name:
            return None

        thread = await self._verify_writting_new_channel(message)

        await write_new_message_log(thread, message)

    async def delete_to_logs(self, message: discord.Message) -> None:
        if str(message.channel.name) == self.logs_channel_name:
            return None

        thread = await self._verify_writting_new_channel(message)

        await write_deleted_message_log(thread, message)

    async def edit_to_logs(self, before: discord.Message, after: discord.Message) -> None:
        if str(before.channel.name) == self.logs_channel_name:
            return None

        thread = await self._verify_writting_new_channel(before)

        await write_edited_message_log(thread, before, after)

    async def _verify_writting_new_channel(self, message: discord.Message) -> discord.Thread:
        if self.log_channel is None:
            self.log_channel = discord.utils.get(self.client.get_all_channels(), name=self.logs_channel_name)

        messages = self.log_channel.history()
        contents = []
        async for m in messages:
            if message.channel.name == m.content:
                return m.thread

            contents.append(str(m.content))

        if message.channel.name not in contents:
            thread = await self.log_channel.create_thread(name=message.channel.name,
                                                          type=discord.ChannelType.public_thread)

            return thread
