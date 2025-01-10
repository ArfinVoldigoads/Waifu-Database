from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import user_collection, collection
from shivu import shivuu as app

DEV_LIST = [6995317382]

# Rarity Map
rarity_map = {
    1: "⚪ Common", 2: "🟠 Rare", 3: "🟢 Medium", 4: "🟡 Legendary", 
    5: "💮 Special Edition", 6: "🔮 Mythical", 7: "🎐 Celestial", 
    8: "❄️ Premium Edition", 9: "🫧 X Verse", 10: "🎭 Immortal"
}

# Fungsi Menghapus Karakter
async def kill_character(character_id):
    character = await collection.find_one({'id': character_id})
    if character:
        try:
            await user_collection.update_many(
                {'characters.id': character_id},
                {'$pull': {'characters': {'id': character_id}}}
            )
            return f"Successfully removed character `{character_id}` from all users."
        except Exception as e:
            print(f"Error updating users: {e}")
            raise
    else:
        raise ValueError("Character not found.")

# Fungsi Mengupdate Karakter
async def update_character_field(user_id, character_id, field, value):
    user = await user_collection.find_one({'id': user_id})
    if user:
        characters = user.get('characters', [])
        for character in characters:
            if character['id'] == character_id:
                character[field] = value
                await user_collection.update_one(
                    {'id': user_id},
                    {'$set': {'characters': characters}}
                )
                return f"Successfully updated `{field}` to `{value}` for character `{character_id}`."
        return f"Character `{character_id}` not found for user `{user_id}`."
    else:
        return f"User `{user_id}` not found."

# Handler untuk /kill
@app.on_message(filters.command(["kill"]) & filters.user(DEV_LIST))
async def remove_character_by_id(client, message):
    try:
        character_id = str(message.text.split()[1])
    except IndexError:
        await message.reply_text("Please provide a character ID.")
        return

    try:
        result_message = await kill_character(character_id)
        await message.reply_text(result_message)
    except ValueError as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in /kill: {e}")
        await message.reply_text("An error occurred while processing the command.")

# Handler untuk /update
@app.on_message(filters.command(["udate"]) & filters.user(DEV_LIST))
async def update_character_by_id(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            await message.reply_text("Usage: /update {user_id} {character_id}")
            return

        user_id = int(args[1])
        character_id = int(args[2])

        user = await user_collection.find_one({'id': user_id})
        if not user:
            await message.reply_text(f"User `{user_id}` not found.")
            return

        characters = user.get('characters', [])
        character = next((c for c in characters if c['id'] == character_id), None)

        if not character:
            await message.reply_text(f"Character `{character_id}` not found for user `{user_id}`.")
            return

        name = character.get('name', 'Unknown')
        anime = character.get('anime', 'Unknown')
        rarity = rarity_map.get(character.get('rarity', 1), "Unknown")

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Update Name", callback_data=f"update_name:{user_id}:{character_id}"),
                InlineKeyboardButton("Update Anime", callback_data=f"update_anime:{user_id}:{character_id}")
            ],
            [
                InlineKeyboardButton("Update Rarity", callback_data=f"update_rarity:{user_id}:{character_id}")
            ]
        ])

        await client.send_photo(
            chat_id=message.chat.id,
            photo=character.get('img_url', 'https://via.placeholder.com/150'),
            caption=(
                f"**Name:** {character.get('name', 'Unknown')}\n"
                f"**Anime:** {character.get('anime', 'Unknown')}\n"
                f"**Rarity:** {rarity_map.get(character.get('rarity', 1), 'Unknown')}\n"
                f"**ID:** {character.get('id', 'Unknown')}"
             ),
             reply_markup=buttons
           )
    except ValueError:
        await message.reply_text("Invalid user ID or character ID.")
    except Exception as e:
        print(f"Error in /update: {e}")
        await message.reply_text("An error occurred while processing the command.")

# Callback untuk Update
@app.on_callback_query(filters.regex(r"^update_(name|anime|rarity):(\d+):(\d+)"))
async def handle_update_callback(client, callback_query):
    action, user_id, character_id = callback_query.data.split(":")
    user_id, character_id = int(user_id), int(character_id)

    if action == "update_name":
        await callback_query.message.reply_text("Send the new name for the character.")
        # Tambahkan logika untuk menangani input nama baru
    elif action == "update_anime":
        await callback_query.message.reply_text("Send the new anime title for the character.")
        # Tambahkan logika untuk menangani input anime baru
    elif action == "update_rarity":
        rarity_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(rarity, callback_data=f"set_rarity:{user_id}:{character_id}:{key}")]
            for key, rarity in rarity_map.items()
        ])
        await callback_query.message.reply_text("Select a new rarity:", reply_markup=rarity_buttons)

# Callback untuk Mengubah Rarity
@app.on_callback_query(filters.regex(r"^set_rarity:(\d+):(\d+):(\d+)"))
async def set_new_rarity(client, callback_query):
    user_id, character_id, rarity_key = map(int, callback_query.data.split(":")[1:])
    result_message = await update_character_field(user_id, character_id, 'rarity', rarity_key)

    await callback_query.answer("Rarity updated successfully!", show_alert=True)
    await callback_query.message.edit_caption(result_message)
