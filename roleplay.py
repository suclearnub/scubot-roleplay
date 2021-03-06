import discord
from tinydb import TinyDB, Query
from modules.botModule import BotModule
import shlex
from datetime import datetime, timedelta
import time
from dateutil.parser import parse

class Roleplay(BotModule):
        name = 'roleplay'

        description = 'Provides useful functions for role-playing games.'

        date_format = '%Y-%m-%d'

        help_text = 'Usage:\n' \
                    '!rp bio charactername - shows character sheet. You will be prompted to make a new one if the character does not exist. \n' \
                    '-  !rp bio new ... - Insert new character with this EXACT ordering: !rp bio new name gender species status age height weight desc pic colour \n' \
                    '-  !rp bio edit ... - Edits character. Use EXACT ordering as !rp bio new. You can only edit if you are the creator of the entry.' \
                    'You must be careful with quotation marks! Use "" if any argument has multiple words.\n\n' \
                    '!rp day - Progresses the roleplay channel to the next day.\n' \
                    '-  !rp day - Shows current date (server-wide for now)\n' \
                    '-  !rp day edit ' + date_format + ' - Edits the date to the new date.\n' \
                    '-  !rp day + - Increments day to next day\n' \
                    '-  !rp day all - Shows dates in all channels\n\n' \
                    '!rp setting newlocation - changes setting of the roleplay channel to another location.'

        trigger_string = 'rp'

        next_day_role = ['@everyone'] # Which role is allowed to edit dates. You can use '@everyone'.

        remove_day_role = ['@everyone'] # Which role is allowed to remove dates. You can use '@everyone' (but why??)

        channel_desc_prefix = 'Current date: ' # Prefix before the current date as shown in the channel description

        module_version = '0.1.0'

        date_colour = 0xBADA55 # Colour of the date embed

        def is_valid_date(self, x):
            try:
                datetime.strptime(x, self.date_format)
                return True
            except ValueError:
                return False

        async def update_channel_description(self, message, client, date):
            try:
                await client.edit_channel(message.channel, topic=self.channel_desc_prefix + date)
                msg = "[:ok_hand:] Updated channel description successfully."
                await client.send_message(message.channel, msg)
            except Exception:
                msg = "[!] Could not update channel description to match current date. Please update manually, and allow the bot to do so in the future. "
                await client.send_message(message.channel, msg)

        async def parse_command(self, message, client):
            msg = shlex.split(message.content)
            roleplay_query = Query()
            if len(msg) > 1:
                if msg[1] == 'bio':
                    table = self.module_db.table('bio')
                    if msg[2] == 'new':
                        if len(msg) > 3:
                            if len(msg) != 13:
                                msg = "[!] Bad data. Check your data ordering."
                                await client.send_message(message.channel, msg)
                            elif table.get(roleplay_query.name == msg[3]) is not None:
                                # Then the character already exists. No dupes!
                                msg = "[!] This character already exists. Did you mean `edit`?"
                                await client.send_message(message.channel, msg)
                            else:
                                table.insert({'name': msg[3], 'gender': msg[4], 'species': msg[5], 'status': msg[6], 'age': msg[7], 'height': msg[8], 'weight': msg[9], 'desc': msg[10], 'pic': msg[11], 'author': message.author.name, 'colour': int(msg[12], 16), 'authorid': message.author.id})
                                msg = "[:ok_hand:] Entry added."
                                await client.send_message(message.channel, msg)
                        else:
                            msg = "[!] You did not provide any information."
                            await client.send_message(message.channel, msg)
                    elif msg[2] == 'edit':
                        if len(msg) > 3:
                            if len(msg) != 13:
                                msg = "[!] Bad data. Check your data ordering."
                                await client.send_message(message.channel, msg)
                            else:
                                if table.get(roleplay_query.name == msg[3]) is None:
                                    # The character does not exist. How do you edit THAT?
                                    msg = "[!] This character does not exist."
                                    await client.send_message(message.channel, msg)
                                elif table.get(roleplay_query.name == msg[3])['authorid'] != message.author.id:
                                    # They're not the author of that bio sheet
                                    msg = "[!] You do not have permission to edit this."
                                    await client.send_message(message.channel, msg)
                                else:
                                    table.update({'name': msg[3], 'gender': msg[4], 'species': msg[5], 'status': msg[6], 'age': msg[7], 'height': msg[8], 'weight': msg[9], 'desc': msg[10], 'pic': msg[11], 'author': message.author.name, 'colour': int(msg[12], 16), 'authorid': message.author.id}, roleplay_query.name == msg[3])
                                    msg = "[:ok_hand:] Entry updated."
                                    await client.send_message(message.channel, msg)
                        else:
                            msg = "[!] You did not provide any information."
                            await client.send_message(message.channel, msg)
                    elif msg[2] == 'rm':
                        if len(msg) > 3:
                            if table.get(roleplay_query.name == msg[3]) is not None:
                                if table.get(roleplay_query.name == msg[3])['authorid'] == message.author.id:
                                    table.remove(roleplay_query.name == msg[3])
                                    msg = "[:ok_hand:] Removed character."
                                    await client.send_message(message.channel, msg)
                                else:
                                    msg = "[!] You do not have permission to remove this."
                                    await client.send_message(message.channel, msg)
                            else:
                                msg = "[!] This character does not exist."
                                await client.send_message(message.channel, msg)
                        else:
                            msg = "[!] You did not provide any information."
                            await client.send_message(message.channel, msg)
                    else:
                        if table.get(roleplay_query.name == msg[2]) is None:
                            # Then this character does not exist.
                            msg = "[!] This character does not exist."
                            await client.send_message(message.channel, msg)
                        else:
                            character = table.get(roleplay_query.name == msg[2])
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
                                if len(msg) > 3:
                                    if self.is_valid_date(msg[3]):
                                        desc_date = msg[3]
                                        if table.get(roleplay_query.channel == message.channel.id) is None:
                                            # There is no date set up yet.
                                            table.insert({'date': msg[3], 'date_actual': int(time.time()), 'last_edit': message.author.name, 'channel': message.channel.id})
                                            msg = "[:ok_hand:] Date has been successfully set."
                                            await client.send_message(message.channel, msg)
                                            await self.update_channel_description(message, client, desc_date)
                                        else:
                                            # There is a date!
                                            table.update({'date': msg[3], 'date_actual': int(time.time()), 'last_edit': message.author.name, 'channel': message.channel.id}, roleplay_query.channel == message.channel.id)
                                            msg = "[:ok_hand:] Date has been successfully edited."
                                            await client.send_message(message.channel, msg)
                                            await self.update_channel_description(message, client, desc_date)
                                    else:
                                        msg = "[!] Bad date format. The current date format is set to: " + self.date_format + "."
                                        await client.send_message(message.channel, msg)
                                else:
                                    msg = "[!] No date specified."
                                    await client.send_message(message.channel, msg)
                            else:
                                msg = "[!] You do not have permissions to edit the time."
                                await client.send_message(message.channel, msg)
                        elif msg[2] == '+':
                            if any(i in author_roles for i in self.next_day_role):
                                new_day = parse(table.get(roleplay_query.channel == message.channel.id)['date']) + timedelta(days=1)
                                table.update({'date': datetime.strftime(new_day, self.date_format), 'date_actual': int(time.time()), 'last_edit': message.author.name, 'channel': message.channel.id}, roleplay_query.channel == message.channel.id)
                                msg = "[:ok_hand:] Date incremented to " + datetime.strftime(new_day, self.date_format) + "."
                                await client.send_message(message.channel, msg)
                                await self.update_channel_description(message, client, datetime.strftime(new_day, self.date_format))
                            else:
                                msg = "[!] You do not have permission to advance the time."
                                await client.send_message(message.channel, msg)
                        elif msg[2] == 'rm':
                            if any(i in author_roles for i in self.next_day_role):
                                if len(msg) > 3:
                                    if table.get(roleplay_query.channel == msg[3]) is not None:
                                        table.remove(roleplay_query.channel == msg[3])
                                        msg = "[:ok_hand:] Removed date in that channel."
                                        await client.send_message(message.channel, msg)
                                    else:
                                        msg = "[!] That channel does not have an existing date."
                                        await client.send_message(message.channel, msg)
                                else:
                                    msg = "[!] No channel to remove specified."
                                    await client.send_message(message.channel, msg)
                            else:
                                msg = "[!] You do not have permissions to remove dates."
                                await client.send_message(message.channel, msg)
                        elif msg[2] == 'all':
                            text = ''
                            if len(table) != 0:
                                for entry in table:
                                    channel = discord.Client.get_channel(client, entry['channel'])
                                    if channel is None:
                                        # The channel has disappeared.
                                        channel_name = entry['channel'] + ' (Missing channel)'
                                        channel_id = entry['channel']
                                    else:
                                        channel_name = channel.name
                                        channel_id = channel.id
                                    text += '#' + channel_name + '\n' \
                                            'ID: ' + channel_id + '\n' \
                                            'Date: ' + entry['date'] + '\n' \
                                            'Last changed: ' + datetime.fromtimestamp(entry['date_actual']).strftime(self.date_format + ' %X') + ' GMT \n' \
                                            'Edited by: ' + entry['last_edit'] + '\n' \
                                            '\n\n'
                                embed = discord.Embed(title='Overview', description=text, colour=self.date_colour)
                                await client.send_message(message.channel, embed=embed)
                            else:
                                msg = "[!] No date set for any channels."
                                await client.send_message(message.channel, msg)
                    else:
                        # It can only be !rp day
                        if table.get(roleplay_query.channel == message.channel.id) is None:
                            msg = "[!] No date set for this channel."
                            await client.send_message(message.channel, msg)
                        else:
                            date_info = table.get(roleplay_query.channel == message.channel.id)
                            text = 'Last changed: ' + datetime.fromtimestamp(date_info['date_actual']).strftime(self.date_format + ' %X') + ' GMT \n' \
                                   'Edited by: ' + date_info['last_edit'] + '\n'
                            embed = discord.Embed(title=date_info['date'], description=text, colour=self.date_colour)
                            await client.send_message(message.channel, embed=embed)
                else:
                    pass
            else:
                pass
