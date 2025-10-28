from pprint import pprint

import discord
import os
import json
import datetime

import nextcloud_access

db_path = "uid_to_discord.json"
UID_TO_DISCORD = json.load(open(db_path))

PROJECT_ID = "suturo25/26"

CHANNEL_ID = os.environ["DEADLINE_CHANNEL_ID"]
#CHANNEL_ID = 1432667618472493151
BOT_TOKEN = os.environ["DEADLINE_REMINDER_BOT_TOKEN"]


def start_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    client = Client(intents=intents)
    client.run(BOT_TOKEN)


def to_timestamp(date_time):
    if date_time is None:
        return None
    return int(datetime.datetime.strptime(date_time.split("+")[0], "%Y-%m-%dT%H:%M:%S").timestamp())


def get_tasks(discord_user):
    mention_string = f"----------------------------------------------\n{discord_user.mention}\n\n"
    task_string = "You are not part of the task board!"

    for user in UID_TO_DISCORD[PROJECT_ID]:
        if user["discord"] == discord_user.id:
            task_string = ""
            work_stacks = nextcloud_access.fetch_work_stack()
            for stack in work_stacks:
                task_string += f"__{stack}__\n"
                for task in work_stacks[stack]:
                    if user["uid"] in task["assignedUsers"]:
                        due_date = to_timestamp(task.get("duedate"))
                        due_date_string = f"due <t:{due_date}> <t:{due_date}:R>"
                        if due_date is None:
                            due_date_string = ""
                        task_string += f" - [**{task["title"]}**](<{nextcloud_access.NEXTCLOUD_USER_URL}\\card\\{task["id"]}>) {due_date_string}\n"
                task_string += "\n"

    return mention_string + task_string


class Client(discord.Client):

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith("!tasks"):
            await message.channel.send(get_tasks(message.author))
        await self.cleanup()

    async def cleanup(self):
        users = {}
        async for message in self.get_channel(int(CHANNEL_ID)).history():
            if message.author == self.user:
                user_id = message.content.split("\n")[1]
                if user_id not in users:
                    users[user_id] = message.id
                else:
                    await message.delete()
            else:
                await message.delete()

        del users

