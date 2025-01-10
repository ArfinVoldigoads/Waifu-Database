import os
import urllib.request
from pymongo import ReturnDocument
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, collection, user_collection, db, CHARA_CHANNEL_ID

# Peta Rarity
RARITY_MAP = {
    1: "⚪ Common",
    2: "🟠 Rare",
    3: "🟢 Medium",
    4: "🟡 Legendary",
    5: "💮 Special Edition",
    6: "🔮 Mythical",
    7: "🎐 Celestial",
    8: "❄️ Premium Edition",
    9: "🫧 X Verse",
    10: "🎭 Immortal"
}

# Peta Kategori
CATEGORY_MAP = {
    '🏖': '🏖𝒔𝒖𝒎𝒎𝒆𝒓 🏖',
    '👘': '👘𝑲𝒊𝒎𝒐𝒏𝒐👘',
    '🧹': '🧹𝑴𝒂𝒊𝒅🧹',
    '🐰': '🐰𝑩𝒖𝒏𝒏𝒚🐰',
    # Tambahkan kategori lainnya jika perlu...
}

# Fungsi untuk mendapatkan kategori
def get_category(name):
    for emoji in CATEGORY_MAP:
        if emoji in name:
            return CATEGORY_MAP[emoji]
    return ""

# Fungsi utama untuk memperbarui karakter
async def update_character(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    try:
        # Parse argumen
        args = context.args
        if len(args) != 3:
            await update.message.reply_text(
                "Incorrect format. Please use: /update id field new_value"
            )
            return

        character_id = args[0]
        field = args[1]
        new_value = args[2].replace("-", " ").title()

        # Validasi field
        valid_fields = ["img_url", "name", "anime", "rarity", "category"]
        if field not in valid_fields:
            await update.message.reply_text(
                f"Invalid field. Valid fields are: {', '.join(valid_fields)}"
            )
            return

        # Proses rarity dan category jika ada
        if field == "rarity":
            new_value = RARITY_MAP.get(int(args[2]), args[2])
        elif field == "category":
            new_value = get_category(args[2]) or args[2]

        # Update di koleksi utama
        updated_character = await collection.find_one_and_update(
            {"id": character_id},
            {"$set": {field: new_value}},
            return_document=ReturnDocument.AFTER,
        )

        if not updated_character:
            await update.message.reply_text("Character not found in the main collection.")
            return

        # Update di user_collection
        await user_collection.update_many(
            {"characters.id": character_id},
            {"$set": {f"characters.$.{field}": new_value}}
        )

        # Update pesan di channel (jika ada)
        if field in ["name", "rarity", "anime", "category"]:
            caption = (
                f"OwO! New Waifu Update!\n\n"
                f"{updated_character['anime']}\n"
                f"{updated_character['id']}: {updated_character['name']}\n"
                f"(𝙍𝘼𝙍𝙄𝙏𝙔: {updated_character['rarity']})\n"
            )
            if updated_character["category"]:
                caption += f"\n{updated_character['category']}\n"
            caption += f"\n➼ ᴜᴘᴅᴀᴛᴇ ʙʏ: <a href=\"tg://user?id={update.effective_user.id}\">{update.effective_user.first_name}</a>"

            try:
                await context.bot.edit_message_caption(
                    chat_id=CHARA_CHANNEL_ID,
                    message_id=updated_character["message_id"],
                    caption=caption,
                    parse_mode="HTML",
                )
            except Exception as e:
                await update.message.reply_text(
                    f"Character updated, but unable to edit message in channel. Error: {str(e)}"
                )

        await update.message.reply_text(f"Character `{character_id}` updated successfully.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

# Tambahkan handler ke aplikasi
application.add_handler(CommandHandler("udate", update_character))
