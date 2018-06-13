import discord
from modules.botModule import *
import shlex
import time
import asyncio
import base64


class AutoAlt(BotModule):
    name = 'autoalt'

    description = 'Automated in-character speech.'

    help_text = '`!say [character] [message]` - allows you to say something for your character. \n' \
                '`!say new [charactername] [bot_token]` - adds a new character for use. \n' \
                '`!say remove [charactername]` - removes a character that you own. \n' \
                '`!say invite [charactername]` - get help with adding a character to this server.\n' \
                '`!say help` - help with making a new bot'

    trigger_string = 'say'

    module_version = '1.0.0'

    listen_for_reaction = False

    protected_names = ['new', 'remove', 'invite'] # These are protected names reserved for the bot.

    global test
    test = discord.Client()

    @test.event
    async def on_ready():
        print("ready")
        print(test.user.name)
        try:
            await test.logout()
        except TypeError:
            pass
        print("logged out")

    async def login_test(self, token, tclient):
        try:
            await tclient.start(token)
            print("it works")
            tclient._closed.clear()
            tclient.http.recreate()
            return True
        except discord.LoginFailure:
            return False

    async def parse_command(self, message, client):
        #test = discord.Client() # We have to reset it unfortunately
        target = Query()
        msg = shlex.split(message.content)
        if msg[1] == 'new':
            if len(msg) >= 4:
                msg[2] = msg[2].lower()
                if msg[2] in self.protected_names:
                    send_msg = "[!] The character you are trying to create is a protected name. Please choose another name."
                    await client.send_message(message.channel, send_msg)
                    return 0
                if self.module_db.get(target.name == msg[2]) is not None:
                    send_msg = "[!] This character already exists. Please choose another name."
                    await client.send_message(message.channel, send_msg)
                    return 0
                send_msg = "I will now test login credentials."
                login_message = await client.send_message(message.channel, send_msg)
                if not await self.login_test(msg[3], test):
                    send_msg = "[!] Could not log in to that character's account. Perhaps your token is wrong?"
                    await client.edit_message(login_message, send_msg)
                    return 0
                bot_id = base64.b64decode(msg[3].split(".")[0]).decode('utf-8')
                self.module_db.insert({'name': msg[2], 'token': msg[3], 'userid': message.author.id, 'botid': bot_id})
                send_msg = "[:ok_hand:] Character added."
                await client.edit_message(login_message, send_msg)
            else:
                send_msg = "[!] Missing arguments."
                await client.send_message(message.channel, send_msg)
        elif msg[1] == 'remove':
            pass
        elif msg[1] == 'invite':
            if len(msg) >= 3:
                msg[2] = msg[2].lower()
                if self.module_db.get(target.name == msg[2]) is None:
                    send_msg = "[!] This character does not exist."
                    await client.send_message(message.channel, send_msg)
                    return 0
                character = self.module_db.get(target.name == msg[2])
                if not await self.login_test(character['token'], test):
                    send_msg = "[!] Could not log in to that character's account. Perhaps your token is wrong?"
                    await client.edit_message(login_message, send_msg)
                    return 0
                perm = discord.Permissions.text()
                url = discord.utils.oauth_url(character['botid'], permissions=perm, server=None, redirect_uri=None)
                send_msg = "Please give this link to the server owner and set up all relevant roles. <" + url + ">"
                await client.send_message(message.author, send_msg)
            else:
                send_msg = "[!] Missing arguments."
                await client.send_message(message.channel, send_msg)
        elif msg[1] == 'help':
            pass
        else:
            pass