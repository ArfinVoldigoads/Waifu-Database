from aiogram import Bot, Dispatcher, types
from motor.motor_asyncio import AsyncIOMotorClient
import re
import aiohttp
from aiogram import executor
import asyncio
from datetime import datetime
import time

bot =Bot('6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs')
dp = Dispatcher(bot)

client = AsyncIOMotorClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['anime_db']
collection = db['anime_collection']
group_collection = db['group_collection']

group_settings = {}  # Store the settings for each group
CHANNEL_ID = -1001683394959
SUDO_USER_ID = [6404226395]

async def generate_id():
    for i in range(1, 10000):
        id = str(i).zfill(4)
        if not await collection.find_one({'_id': id}):
            return id
    return None

async def is_url_valid(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except Exception:
        return False





@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    start = time.time()
    sent_message = await message.reply("Pong!")
    end = time.time()
    elapsed_ms = (end - start) * 1000  # convert to milliseconds
    await sent_message.edit_text(f"Pong! Message speed: {int(elapsed_ms)} milliseconds")


@dp.message_handler(commands=['upload'])
async def upload(message: types.Message):
    if message.from_user.id in SUDO_USER_ID:
        try:
            _, img_url, anime_name, character_name = message.text.split(' ')
            character_name = character_name.replace('-', ' ')
            anime_name = anime_name.replace('-', ' ')
            # Validate the URL
            if not await is_url_valid(img_url):
                await message.reply("Invalid URL")
                return
            id = await generate_id()
            if id is None:
                await message.reply("Error: Database is full.")
                return
            doc = {
                '_id': id,
                'img_url': img_url,
                'anime_name': anime_name,
                'character_name': character_name
            }
            await collection.insert_one(doc)
            await message.reply("Successfully uploaded")
            # Send the information to the channel
            sent_message = await bot.send_photo(
                CHANNEL_ID,
                img_url,
                caption=f"<b>ID:</b> {id}\n<b>Anime Name:</b> {anime_name}\n<b>Character Name:</b> {character_name}",
                parse_mode='HTML'
            )
            # Save the message ID to the database
            await collection.update_one({'_id': id}, {'$set': {'channel_message_id': sent_message.message_id}})
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['delete'])
async def delete(message: types.Message):
    if message.from_user.id in SUDO_USER_ID:
        try:
            _, id = message.text.split(' ')
            # Find the character in the database
            doc = await collection.find_one({'_id': id})
            if doc is None:
                await message.reply("Character not found.")
                return
            # Delete the character from the database
            await collection.delete_one({'_id': id})
            # Delete the message from the channel
            await bot.delete_message(CHANNEL_ID, doc['channel_message_id'])
            await message.reply("Successfully deleted.")
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
    else:
        await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['set_frequency'])
async def set_frequency(message: types.Message):
    if message.chat.type != 'private':  # Ensure this command is used in a group
        user = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ('administrator', 'creator'):  # Check user permissions
            await message.reply("You must be an administrator to use this command.")
            return
        try:
            _, frequency = message.text.split(' ')
            frequency = int(frequency)
            if frequency < 1:
                raise ValueError
            # Update the group settings
            group_settings[message.chat.id] = frequency
            await message.reply("Successfully changed the frequency.")
        except ValueError:
            await message.reply("Invalid frequency. Please enter a positive integer.")
from aiogram import types

async def on_any_message(message: types.Message):
    # Check if the message is sent in a group
    if message.chat.type != 'private':
        # Increment the message count for the group
        group_settings[message.chat.id] = group_settings.get(message.chat.id, 0) + 1
        # Check if the message count has reached the frequency
        if group_settings[message.chat.id] >= 100:
            # Reset the message count
            group_settings[message.chat.id] = 0
            # Spawn a character
            doc = await collection.find_one()  # Fetch a character from the database
            if doc is not None:
                await bot.send_photo(
                    message.chat.id,
                    doc['img_url'],
                    caption=f"<b>ID:</b> {doc['_id']}\n<b>Anime Name:</b> {doc['anime_name']}\n<b>Character Name:</b> {doc['character_name']}",
                    parse_mode='HTML'
                )

dp.register_message_handler(on_any_message)






executor.start_polling(dp)
