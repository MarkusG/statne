from datetime import datetime, timezone
import os

import discord
import psycopg2

conn = psycopg2.connect("dbname=discord")

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as {0}'.format(self.user))
        print('Fetching messages')
        dickne = self.get_guild(467775901686431755);
        cur = conn.cursor()
        cur.execute('SELECT timestamp FROM message \
                ORDER BY message.timestamp DESC LIMIT 1;')
        latest = cur.fetchone()[0]
        for channel in dickne.text_channels:
            try:
                async for message in channel.history(limit=None, after=latest):
                    if message.author.bot:
                        continue
                    cur.execute("INSERT INTO message \
                        (id, content, timestamp, channel, guild, author) \
                        VALUES (%s, %s, %s, %s, %s, %s);",
                        [message.id, message.content, message.created_at,
                        message.channel.id, message.guild.id,
                        message.author.id])
                    if len(message.content) > 50:
                        content = (message.content[:25] + '..')
                    else:
                        content = message.content
                    print('{0.channel.name} {0.created_at} {0.author}: {1}'
                            .format(message, content))
            except discord.errors.Forbidden:
                print('cannot read channel {0}'.format(channel.name))

        conn.commit()
        cur.close()
        print('Done fetching messages')


    async def on_message(self, message):
        if not isinstance(message.type, discord.MessageType): # only user msgs
            return
        if message.guild.id != 467775901686431755: # only dickne
            return
        if message.author.bot: # ignore bots
            return
        print('{0.author}: {0.content}'.format(message))
        cur = conn.cursor()
        cur.execute("INSERT INTO message \
            (id, content, timestamp, channel, guild, author) \
            VALUES (%s, %s, %s, %s, %s, %s);",
            [message.id, message.content, message.created_at,
            message.channel.id, message.guild.id, message.author.id])
        conn.commit()
        cur.close()

client = MyClient()
client.run(os.environ['STATNE_TOKEN'])
