import urllib.request
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClient
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, CHARA_CHANNEL_ID, SUPPORT_CHAT

mongo_url = 'mongodb+srv://Husbando:Husbando@cluster0.lai7z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
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

WRONG_FORMAT_TEXT = """Wrong ❌ format... eg. /upload Img_url muzan-kibutsuji Demon-slayer 3

img_url character-name anime-name rarity-number

use rarity number accordingly rarity Map

rarity_map = 1 (⚪️ Common), 2 (🟠 Rare), 3 (🟢 Medium), 4 (🟡 Legendary), 5 (💮 Special Edition), 6 (🔮 Mythical), 7 (🎐 Celestial), 8 (❄️ Premium Edition), 9 (🫧 X Verse)"""

CATEGORY_MAP = {
    '🏖': '🏖𝒔𝒖𝒎𝒎𝒆𝒓 🏖',
    '👘': '👘𝑲𝒊𝒎𝒐𝒏𝒐👘',
    '🧹': '🧹𝑴𝒂𝒊𝒅🧹',
    '🐰': '🐰𝑩𝒖𝒏𝒏𝒚🐰',
    '🏜️': '🏜️𝑬𝒈𝒚𝒑𝒕🏜️',
    '🎒': '🎒𝑺𝒄𝒉𝒐𝒐𝒍🎒',
    '💞': '💞𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆💞',
    '🎃': '🎃𝑯𝒂𝒍𝒍𝒐𝒘𝒆𝒆𝒏🎃',
    '🥻': '🥻𝑺𝒂𝒓𝒆𝒆🥻',
    '💉': '💉𝑵𝒖𝒓𝒔𝒆💉',
    '☃️': '☃️𝑾𝒊𝒏𝒕𝒆𝒓☃️',
    '🎄': '🎄𝑪𝒉𝒓𝒊𝒔𝒕𝒎𝒂𝒔🎄',
    '👥': '👥𝐃𝐮𝐨👥',
    '🤝': '🤝𝐆𝐫𝐨𝐮𝐩🤝',
    '⚽': '⚽𝑭𝒐𝒐𝒕𝒃𝒂𝒍𝒍⚽',
    '🏀': '🏀𝑩𝒂𝒔𝒌𝒆𝒕𝒃𝒂𝒍𝒍🏀',
    '🎩': '🎩𝑻𝒖𝒙𝒆𝒅𝒐🎩',
    '🏮': '🏮𝑪𝒉𝒊𝒏𝒆𝒔𝒆🏮',
    '📙': '📙𝑴𝒂𝒏𝒉𝒘𝒂📙',
    '👙': '👙𝑩𝒊𝒌𝒊𝒏𝒊👙',
    '🎊': '🎊𝑪𝒉𝒆𝒆𝒓𝒍𝒆𝒂𝒅𝒆𝒓𝒔🎊',
    '🎮': '🎮𝑮𝒂𝒎𝒆🎮',
    '💍': '💍𝑴𝒂𝒓𝒓𝒊𝒆𝒅💍',
    '👶': '👶𝑪𝒉𝒊𝒃𝒊👶',
    '🕷️': '🕷️𝑺𝒑𝒊𝒅𝒆𝒓🕷️'
}

def get_category(name):
    for emoji in CATEGORY_MAP:
        if emoji in name:
            return CATEGORY_MAP[emoji]
    return ""

async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']

async def upload(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask My Owner...')
        return

    try:
        args = context.args
        if len(args) != 4:
            await update.message.reply_text(WRONG_FORMAT_TEXT)
            return

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        try:
            urllib.request.urlopen(args[0])
        except:
            await update.message.reply_text('Invalid URL.')
            return

        rarity_map = {1: "⚪ Common", 2: "🟠 Rare", 3: "🟢 Medium", 4: "🟡 Legendary", 5: "💮 Special Edition", 6: "🔮 Mythical", 7: "🎐 Celestial", 8: "❄️ Premium Edition", 9: "🫧 X Verse"}
        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            await update.message.reply_text('Invalid rarity. Please use 1, 2, 3, 4, 5, 6')
            return

        id = str(await get_next_sequence_number('character_id')).zfill(2)
        category = get_category(character_name)

        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'id': id,
            'category': category
        }

        caption = f"OwO! Add New Husband!\n\n{anime}\n{id}: {character_name}\n(𝙍𝘼𝙍𝙄𝙏𝙔: {rarity})\n"
        if category:
            caption += f"\n{category}\n"
        caption += f"\n➼ ᴀᴅᴅᴇᴅ ʙʏ: <a href=\"tg://user?id={update.effective_user.id}\">{update.effective_user.first_name}</a>"

        try:
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=args[0],
                caption=caption,
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
            await collection.insert_one(character)
            await update.message.reply_text('CHARACTER ADDED....')
        except:
            await collection.insert_one(character)
            await update.message.reply_text("Character Added but no Database Channel Found, Consider adding one.")
        
    except Exception as e:
        await update.message.reply_text(f'Character Upload Unsuccessful. Error: {str(e)}\nIf you think this is a source error, forward to: {SUPPORT_CHAT}')

async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask my Owner to use this Command...')
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format... Please use: /delete ID')
            return

        character = await collection.find_one_and_delete({'id': args[0]})
        if character:
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            await update.message.reply_text('DONE')
        else:
            await update.message.reply_text('Deleted Successfully from db, but character not found In Channel')
    except Exception as e:
        await update.message.reply_text(f'{str(e)}')

async def update_character(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Incorrect format. Please use: /update id field new_value')
            return

        # Get character by ID
        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text('Character not found.')
            return

        # Check if field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity', 'category']
        if args[1] not in valid_fields:
            await update.message.reply_text('Invalid field. Valid fields are: img_url, name, anime, rarity, category')
            return

        # Update character
        new_value = args[2].replace('-', ' ').title()
        if args[1] == 'rarity':
            rarity_map = {1: "⚪ Common", 2: "🟠 Rare", 3: "🟢 Medium", 4: "🟡 Legendary", 5: "💮 Special Edition", 6: "🔮 Mythical", 7: "🎐 Celestial", 8: "❄️ Premium Edition", 9: "🫧 X Verse"}
            new_value = rarity_map.get(int(args[2]), args[2])
        elif args[1] == 'category':
            new_value = get_category(args[2]) or args[2]

        updated_character = await collection.find_one_and_update(
            {'id': args[0]},
            {'$set': {args[1]: new_value}},
            return_document=ReturnDocument.AFTER
        )

        if updated_character:
            # Update the message in the channel
            caption = f"OwO! New Husband Update!\n\n{updated_character['anime']}\n{updated_character['id']}: {updated_character['name']}\n(🔮𝙍𝘼𝙍𝙄𝙏𝙔: {updated_character['rarity']})\n"
            if updated_character['category']:
                caption += f"\n{updated_character['category']}\n"
            caption += f"\n➼ ᴜᴘᴅᴀᴛᴇ ʙʏ: <a href=\"tg://user?id={update.effective_user.id}\">{update.effective_user.first_name}</a>"

            try:
                await context.bot.edit_message_caption(
                    chat_id=CHARA_CHANNEL_ID,
                    message_id=updated_character['message_id'],
                    caption=caption,
                    parse_mode='HTML'
                )
                await update.message.reply_text('Character updated successfully.')
            except:
                await update.message.reply_text('Character updated, but unable to edit message in channel.')

        else:
            await update.message.reply_text('Character update unsuccessful.')
    except Exception as e:
        await update.message.reply_text(f'Character update unsuccessful. Error: {str(e)}')

application.add_handler(CommandHandler('upload', upload))
application.add_handler(CommandHandler('dd', delete))
application.add_handler(CommandHandler('update', update_character))
