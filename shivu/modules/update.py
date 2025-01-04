from pyrogram import Client, filters
from shivu import sudo_users
from shivu import shivuu as app
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = 'mongodb+srv://Arfin01:Arfin123@cluster0.e5ccuiv.mongodb.net/?retryWrites=true&w=majority'
lol = AsyncIOMotorClient(mongo_url)
db = lol['Character_catcher']
set_on_data = db['set_on_data']
refeer_collection = db['refeer_collection']
set_off_data = db['set_off_data']
collection = db['anime_characters_lol']
safari_cooldown_collection = db["safari_cooldown"]
safari_users_collection = db["safari_users_collection"]
sudo_users_collection = db["sudo_users_collection"]
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
global_ban_users_collection = db["global_ban_users_collection"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']
banned_groups_collection = db['Banned_Groups']
BANNED_USERS = db['Banned_Users']
registered_users = db['registered_users']

DEV_LIST = [6995317382, 7128714969, 6444201098, 5147271956, 5147271956, 2075516632, 5008662958, 7127913934, 5843270062, 1495261563, 6489025882, 6752263178, 7177727796, 6205444949]


# Fungsi untuk memperbarui karakter
async def update_character(character_id, updates):
    # Cari karakter di collection utama
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            # Perbarui data karakter di collection utama
            await collection.update_one(
                {'id': character_id},
                {'$set': updates}
            )

            # Perbarui data karakter di koleksi pengguna
            await user_collection.update_many(
                {'characters.id': character_id},
                {'$set': {'characters.$[elem]': updates}},
                array_filters=[{'elem.id': character_id}]
            )

            return f"Character `{character_id}` updated successfully."
        except Exception as e:
            print(f"Error updating character: {e}")
            raise
    else:
        raise ValueError("Character not found.")


# Handler untuk perintah /update
@app.on_message(filters.command(["update"]) & filters.user(DEV_LIST))
async def update_character_command(client, message):
    try:
        # Parsing argumen perintah
        args = message.text.split(maxsplit=2)
        character_id = str(args[1])
        update_data = args[2]

        # Parsing parameter pembaruan (-name, -link, -anime)
        updates = {}
        if "-name" in update_data:
            updates['name'] = update_data.split("-name")[1].strip().split()[0]
        if "-link" in update_data:
            updates['img_url'] = update_data.split("-link")[1].strip().split()[0]
        if "-anime" in update_data:
            updates['anime'] = update_data.split("-anime")[1].strip().split()[0]

        if not updates:
            await message.reply_text("Please provide valid update parameters (e.g., -name, -link, -anime).")
            return

        # Perbarui karakter
        result_message = await update_character(character_id, updates)
        await message.reply_text(result_message)

    except IndexError:
        await message.reply_text("Usage: /update {id_character} -name {name} -link {photo_url} -anime {anime_name}")
    except ValueError as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in update_character_command: {e}")
        await message.reply_text("An error occurred while processing the update command.")
