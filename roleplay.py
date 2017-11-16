import discord
from tinydb import TinyDB, Query
from modules.botModule import BotModule
import shlex
from datetime import datetime, timedelta
import time

class Roleplay(BotModule):
        name = 'roleplay'

        description = 'Provides useful functions for role-playing games.'

        help_text = 'Usage:\n' \
                    '!rp bio charactername - shows character sheet. You will be prompted to make a new one if the character does not exist. \n' \
                    '-  !rp bio new ... - Insert new character with this EXACT ordering: !rp bio new name gender species status age height weight desc pic colour \n' \
                    '-  !rp bio edit ... - Edits character. Use EXACT ordering as !rp bio new. You can only edit if you are the creator of the entry.' \
                    'You must be careful with quotation marks! Use "" if any argument has multiple words.\n\n' \
                    '!rp day - Progresses the roleplay channel to the next day.\n' \
                    '-  !rp day - Shows current date (server-wide for now)\n' \
                    '-  !rp day edit newday-newmonth-newyear - Edits the date to the new date.\n' \
                    '-  !rp day + - Increments day to next day\n\n' \
                    '!rp setting newlocation - changes setting of the roleplay channel to another location.'

        trigger_string = 'rp'

        next_day_role = ['Literal Emerald'] # Which role is allowed to edit dates

        date_format = '%Y-%m-%d'

        module_version = '0.1.0'

        date_colour = 0xBADA55 # Colour of the date embed

        def is_valid_date(self, x):
            try:
                datetime.strptime(x, self.date_format)
                return True
            except ValueError:
                return False

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
                                    self.module_db.update({'name': msg[3], 'gender': msg[4], 'species': msg[5], 'status': msg[6], 'age': msg[7], 'height': msg[8], 'weight': msg[9], 'desc': msg[10], 'pic': msg[11], 'author': message.author.name, 'colour': int(msg[12], 16), 'authorid': message.author.id}, roleplay_query.name == msg[3])
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
                elif msg[1] == 'day':
                    author_roles = message.author.roles
                    author_roles = [x.name for x in message.author.roles]
                    table = self.module_db.table('day')
                    if len(msg) > 2:
                    # That means it can only be !rp day foobar...
                        if msg[2] == 'edit':
                            if any(i in author_roles for i in self.next_day_role):
                                if self.is_valid_date(msg[3]):
                                    if self.module_db.get(roleplay_query.channel == message.channel.id) is None:
                                        # There is no date set up yet.
                                        self.module_db.insert({'date': msg[3], 'date_actual': int(time.time()), 'last_edit': message.author.name, 'channel': message.channel.id})
                                        msg = "[:ok_hand:] Date has been successfully set."
                                        await client.send_message(message.channel, msg)
                                    else:
                                        # There is a date!
                                        self.module_db.update({'date': msg[3], 'date_actual': int(time.time()), 'last_edit': message.author.name, 'channel': message.channel.id}, roleplay_query.channel == message.channel.id)
                                        msg = "[:ok_hand:] Date has been successfully edited."
                                        await client.send_message(message.channel, msg)
                                else:
                                    msg = "[!] Bad date format. The current date format is set to: " + self.date_format + "."
                                    await client.send_message(message.channel, msg)
                            else:
                                msg = "[!] You do not have permissions to edit the time."
                                await client.send_message(message.channel, msg)
                        elif msg[2] == '+':
                            if any(i in author_roles for i in self.next_day_role):
                                new_day = datetime.strptime(self.module_db.get(roleplay_query.channel == message.channel.id)['date'], self.date_format) + timedelta(days=1)
                                self.module_db.update({'date': datetime.strftime(new_day, self.date_format), 'date_actual': int(time.time()), 'last_edit': message.author.name, 'channel': message.channel.id}, roleplay_query.channel == message.channel.id)
                                msg = "[:ok_hand:] Date incremented to " + datetime.strftime(new_day, self.date_format) + "."
                                await client.send_message(message.channel, msg)
                            else:
                                msg = "[!] You do not have permission to advance the time."
                                await client.send_message(message.channel, msg)
                    else:
                        # It can only be !rp day
                        if self.module_db.get(roleplay_query.channel == message.channel.id) is None:
                            msg = "[!] No date set for this channel."
                            await client.send_message(message.channel, msg)
                        else:
                            date_info = self.module_db.get(roleplay_query.channel == message.channel.id)
                            text = 'Last changed: ' + datetime.fromtimestamp(date_info['date_actual']).strftime(self.date_format + ' %X') + ' GMT \n' \
                                   'Edited by: ' + date_info['last_edit'] + '\n'
                            embed = discord.Embed(title=date_info['date'], description=text, colour=self.date_colour)
                            await client.send_message(message.channel, embed=embed)
                elif msg[1] == 'setting':
                    table = self.module_db.table('setting')
                    # TODO: Change setting of roleplay scene
                else:
                    pass
            else:
                pass
