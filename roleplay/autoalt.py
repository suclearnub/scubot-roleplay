import discord
from modules.botModule import *
import shlex
import time

class AutoAlt(BotModule):
    name = 'autoalt'

    description = 'Automated in-character speech.'

    help_text = '`!say [character] [message]` - allows you to say something for your character. \n' \
                '`!say new [charactername] [bot_token]` - adds a new character for use. \n' \
                '`!say remove [charactername]` - removes a character that you own. \n' \
                '`!say invite [charactername]` - get help with adding a character to this server.\n' \
                '`!say remove [charactername]` - removes a character that you own.'

    trigger_string = 'say'

    module_version = '1.0.0'

    listen_for_reaction = False

    protected_names = ['new', 'remove', 'invite'] # These are protected names reserved for the bot.

    async def login_test(self, token):
        try:
            test_client = discord.Client()
            test_client.run(token)
            test_client.logout
            return True
        except LoginFailure:
            return False


    async def parse_command(self, message, client):
        target = Query()
        msg = shlex.split(message.content)
        if msg[1] == 'new':
            if len(msg) > 4:
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
                if not self.login_test(msg[3]):
                    send_msg = "[!] Could not log in to that character's account. Perhaps your token is wrong?"
                    await client.edit_message(login_message, send_msg)
                    return 0
                self.module_db.insert({'charactername': msg[2], 'token': msg[3], 'userid': message.author.id})
                send_msg = "[:ok_hand:] Character added."
                await client.edit_message(login_message, send_msg)
            else:
                send_msg = "[!] Missing arguments."
                await client.send_message(message.channel, send_msg)
        elif msg[1] == 'remove':
            pass
        elif msg[1] == 'help':
            pass
        else:
            pass