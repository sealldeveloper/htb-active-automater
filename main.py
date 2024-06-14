import discord
import discord.ext
from discord.ext import tasks
import datetime
from dotenv import load_dotenv, dotenv_values
import os
import requests
from aiohttp import ClientSession
from io import BytesIO
from time import sleep
from tinydb import TinyDB, Query, operations
db = TinyDB('db.json')
query = Query()

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Load environment variables
load_dotenv()

# Environment Variables
htb_api_token = os.getenv('HTB_API_TOKEN') if os.getenv('HTB_API_TOKEN') else None
discord_token = os.getenv("DISCORD_TOKEN") if os.getenv('DISCORD_TOKEN') else None
discord_guild_id = os.getenv("DISCORD_GUILD_ID") if os.getenv('DISCORD_GUILD_ID') else None

# Miscellaneous Variables
description = '''A Discord bot to create and manage posts for active HTB machines

Made by se.al / sealldeveloper'''

headers = {
    'User-Agent': 'HackTheBox Discord Active Machine Bot',
    'Authorization': f'Bearer {htb_api_token}'
}

if not db.all():
    db.insert({'machines':{},'config':{'posts':{},'setup_complete':True}})

# setting up the bot
intents = discord.Intents.default()
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

htb_api_uri = 'https://www.hackthebox.com/api/v4/machine/paginated?per_page=100'

### FUNCTIONS ###

async def getActiveMachines():
    try:
        active_machines_list = requests.request("GET", htb_api_uri, headers=headers, data={})

        machines_data = active_machines_list.json()
        machines_db = db.all()[0]['machines']
        cur_ids = list(machines_db.keys())
        new_ids = set()
        logging.info('Getting new active machines...')
        for machine in machines_data['data']:
            new_ids.add(machine['id'])
            if machine['id'] not in cur_ids:
                machines_db[machine['id']] = {'name':machine['name'],'diff':machine['difficultyText'],'os':machine['os'],'avatar':machine['avatar']}
        for curid in cur_ids:
            if curid not in new_ids:
                del machines_db[curid]
        db.update({'machines':machines_db})
        logging.info('Got active machines!')
    except Exception as e:
        logging.exception(f'Error updating posts: {e}')

async def createPosts():
    config_db = db.all()[0]['config']
    config_keys = config_db.keys()
    posts_keys = set(config_db['posts'].keys())
    
    machines_db = db.all()[0]['machines']
    machines_keys = machines_db.keys()

    forum_channel = client.get_channel(int(config_db['channel_id']))
    logging.info('Making new posts...')
    for machine_id in reversed(list(machines_keys)):
        if machine_id not in posts_keys:

            diff_tag = discord.utils.get(forum_channel.available_tags, name=machines_db[machine_id]['diff'])
            os_tag = discord.utils.get(forum_channel.available_tags, name=machines_db[machine_id]['os'])
            image_url = f"https://labs.hackthebox.com{machines_db[machine_id]['avatar']}"
            async with ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        logging.info("ERR: Failed to download image")
                        return

                    image_data = BytesIO(await resp.read())
                    
                    # Create a new post with the image
                    post = await forum_channel.create_thread(
                        name=f"{machines_db[machine_id]['name']} - #{machine_id}",
                        content=f"This is a **{machines_db[machine_id]['os']}** box of **{machines_db[machine_id]['diff']}** difficulty.\n\nYou can attempt the box [here](https://app.hackthebox.com/machines/{machines_db[machine_id]['name'].replace(' ','%20')})\n\n**__Please do not share anything major about the box until the first 24 hours has passed, then hints are OK!__**",
                        file=discord.File(image_data, "logo.png"),
                        applied_tags=[os_tag, diff_tag]
                    )

                    config_db['posts'][machine_id] = post[0].id
    logging.info('Retiring old posts...')
    for machine_id in posts_keys:
        if machine_id not in machines_keys:
            logging.info(f"Retiring #{machine_id}...")
            post = await forum_channel.get_thread(config_db['posts'][machine_id])
            if post:
                await post.edit(name=f'[RETIRED] {post.name}')
                del config_db['posts'][machine_id]
    
    db.update({'config':config_db})
            
def start_update_posts_task():
    if not update_posts.is_running():
        logging.info('Starting update_posts task...')
        update_posts.start()
    else:
        logging.info('Restarting update_posts task...')
        update_posts.restart()

### TASKS ###

@tasks.loop(hours=1)
async def update_posts():
    try:
        config_db = db.all()[0]['config']
        config_keys = config_db.keys()
        if 'channel_id' in config_keys:
            logging.info('Getting current active machines...')
            await getActiveMachines()
            logging.info('Updating posts...')
            await createPosts()
            logging.info('Posts updated successfully.')
        else:
            logging.info('Setup not complete, skipping update...')
    except Exception as e:
        logging.exception(f'Error updating posts: {e}')

### COMMANDS ###

@tree.command(name="setup", description="Setup the forum channel, tags and initial posts.",guild=discord.Object(id=discord_guild_id))
async def slash_command(interaction: discord.Interaction):    
    await interaction.response.defer(ephemeral=True)
    logging.info(f'[{interaction.user.id}] - ran {interaction.command.name}')
    if interaction.user.guild_permissions.administrator or organiserrole in interaction.user.roles:
        os_tags = ['Windows', 'Linux', 'FreeBSD', 'OpenBSD', 'Other']
        diff_tags = ['Easy', 'Medium', 'Hard', 'Insane']

        guild = interaction.guild

        config_db = db.all()[0]['config']
        config_keys = config_db.keys()

        if 'channel_id' in config_keys:
            await interaction.edit_original_response(content=f'Erasing old config...')
            try:
                forum_channel = client.get_channel(config_db['channel_id'])
                await forum_channel.delete()
                del config_db['channel_id']
            except:
                return await interaction.edit_original_response(content=f'Could not delete old forum channel!')
        if 'posts' in config_keys:
            config_db['posts'] = {}

        try:
            await interaction.edit_original_response(content=f'Creating forum channel...')
            forum_channel = await guild.create_forum(
                name="hackthebox-machines",
                reason="For discussing current HTB machines in a server"
            )
            config_db['channel_id'] = forum_channel.id
        except:
            return await interaction.edit_original_response(content=f'Could not create forum channel!')

        try:
            await interaction.edit_original_response(content=f'Making tags...')
            for tag in os_tags:
                await forum_channel.create_tag(name=tag, moderated=False)
            for tag in diff_tags:
                await forum_channel.create_tag(name=tag, moderated=False)
        except:
            return await interaction.edit_original_response(content=f'Could not create tags!')
        db.update({'config':config_db})

        start_update_posts_task()

        await interaction.edit_original_response(content=f'Setup complete! See <#{forum_channel.id}>.')
    else:
        return await interaction.edit_original_response(content='You are not an admin!')

### EVENTS ###

@client.event
async def on_ready():
    logging.info(f'Syncing trees...')
    await tree.sync(guild=discord.Object(id=int(discord_guild_id)))
    # print "ready" in the console when the bot is ready to work
    logging.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logging.info('------')
    start_update_posts_task()
        



client.run(discord_token)
