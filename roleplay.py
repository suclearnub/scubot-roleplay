import discord
from tinydb import TinyDB, Query
from modules.botModule import BotModule
import shlex

class Roleplay(BotModule):
        name = 'roleplay'

        description = 'Provides useful functions for role-playing games.'

        help_text = 'Usage:\n' \
                    '!rp bio charactername - shows character sheet. You will be prompted to make a new one if the character does not exist. \n' \
                    '-  !rp bio new ... - Insert new character with this EXACT ordering: !rp bio new name gender species status age height weight desc pic colour \n' \
                    '-  !rp bio edit ... - Edits character. Use EXACT ordering as !rp bio new. You can only edit if you are the creator of the entry.' \
                    'You must be careful with quotation marks! Use "" if any argument has multiple words.\n' \
                    '!rp nextday summary[optional] - progresses the roleplay channel to the next day.\n' \
                    '!rp setting newlocation - changes setting of the roleplay channel to another location.'

        trigger_string = 'rp'

        module_version = '0.1.0'

        async def parse_command(self, message, client):
            msg = shlex.split(message.content)
            roleplay_query = Query()
            if len(msg) > 1:
                if msg[1] == 'bio':
                    table = self.module_db.table('bio')
                    if msg[2] == 'new':
                        if len(msg) > 3:
                            if len(msg) != 13:
                                msg = "[!] You did not provide enough information."
                                await client.send_message(message.channel, msg)
                            else:
                                self.module_db.insert({'name': msg[3], 'gender': msg[4], 'species': msg[5], 'status': msg[6], 'age': msg[7], 'height': msg[8], 'weight': msg[9], 'desc': msg[10], 'pic': msg[11], 'author': message.author.name, 'colour': int(msg[12], 16), 'authorid': message.author.id})
                                msg = "[:ok_hand:] Entry added."
                                await client.send_message(message.channel, msg)
                        else:
                            msg = "[!] You did not provide any information."
                            await client.send_message(message.channel, msg)
                    elif msg[2] == 'edit':
                        if len(msg) > 3:
                            if len(msg) != 13:
                                msg = "[!] You did not provide enough information."
                                await client.send_message(message.channel, msg)
                            else:
                                if self.module_db.get(roleplay_query.name == msg[3]) is None:
                                    # The character does not exist. How do you edit THAT?
                                    msg = "[!] This character does not exist."
                                    await client.send_message(message.channel, msg)
                                elif self.module_db.get(roleplay_query.name == msg[3])['authorid'] != message.author.id:
                                    # They're not the author of that bio sheet
                                    msg = "[!] You do not have permission to edit this."
                                    await client.send_message(message.channel, msg)
                                else:
                                    self.module_db.update({'name': msg[3], 'gender': msg[4], 'species': msg[5], 'status': msg[6], 'age': msg[7], 'height': msg[8], 'weight': msg[9], 'desc': msg[10], 'pic': msg[11], 'author': message.author.name, 'colour': int(msg[12], 16), 'authorid': message.author.id})
                                    msg = "[:ok_hand:] Entry updated."
                                    await client.send_message(message.channel, msg)
                        else:
                            msg = "[!] You did not provide any information."
                            await client.send_message(message.channel, msg)
                    else:
                        if self.module_db.get(roleplay_query.name == msg[2]) is None:
                            # Then this character does not exist.
                            msg = "[!] This character does not exist."
                            await client.send_message(message.channel, msg)
                        else:
                            character = self.module_db.get(roleplay_query.name == msg[2])
                            text = 'By: ' + character['author'] + '\n' \
                                   'Gender: ' + character['gender'] + '\n' \
                                   'Species: ' + character['species'] + '\n' \
                                   'Status: ' + character['status'] + '\n' \
                                   'Age: ' + character['age'] + '\n' \
                                   'Height: ' + character['height'] + '\n' \
                                   'Weight: ' + character['weight'] + '\n' \
                                   'Description: ' + character['desc'] + '\n'
                            embed = discord.Embed(title=character['name'], description=text, colour=character['colour'])
                            embed.set_image(url=character['pic'])
                            await client.send_message(message.channel, embed=embed)
                elif msg[1] == 'nextday':
                    table = self.module_db.table('day')
                    # TODO: Progress to next day
                    pass
                elif msg[1] == 'setting':
                    table = self.module_db.table('setting')
                    # TODO: Change setting of roleplay scene
                else:
                    pass
            else:
                pass
