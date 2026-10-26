import telebot
from telebot import types

TOKEN = "8820381735:AAFbWa7vMbY0hFghFF8vPHwOZtPuJXxbxu4"
bot = telebot.TeleBot(TOKEN)

TARGET_GROUP_ID = -1003951414350      # පබ්ලික් ගෲප් ID එක
SOURCE_CHAT_ID = -5226449370      # ප්‍රයිවට් ගෲප් ID එක

# තාවකාලිකව දත්ත ගබඩා කරගැනීමට
pending_videos = {}  # user_id: video_file_id
video_storage = {}   # msg_id: video_file_id

# ඔබේ GitHub Pages ලින්ක් එක මෙහි ඇත
WEB_URL = "https://byehub.github.io/unlock/"

try:
    bot.remove_webhook()
    print("Old webhook removed successfully.")
except Exception as e:
    print(f"Webhook error: {e}")

# 1. ප්‍රයිවට් ගෲප් එකට වීඩියෝවක් දැමූ විට, ඇඩ්මින්ගේ DM එකට ෆොටෝ එක ඉල්ලා සිටීම
@bot.message_handler(content_types=['video'], func=lambda message: message.chat.id == SOURCE_CHAT_ID)
def ask_for_photo(message):
    user_id = message.from_user.id
    video_file_id = message.video.file_id
    pending_videos[user_id] = video_file_id
    
    try:
        bot.send_message(
            user_id, 
            "🎬 ඔබ ප්‍රයිවට් ගෲප් එකට අලුත් වීඩියෝවක් දැමුවා!\n\n"
            "👇 දැන් මේ සඳහා පබ්ලික් ගෲප් එකට දැමිය යුතු Photo (Thumbnail) එක මෙම චැට් එකට එවන්න:"
        )
    except Exception as e:
        print(f"DM Error: {e}")

# 2. ඔබ DM එකට ෆොටෝ එක එවූ විට, එය පබ්ලික් ගෲප් එකට පෝස්ට් කිරීම
@bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id == message.from_user.id)
def handle_uploaded_photo(message):
    user_id = message.from_user.id
    
    if user_id in pending_videos:
        video_file_id = pending_videos[user_id]
        photo_file_id = message.photo[-1].file_id
        
        msg_id = message.message_id
        video_storage[str(msg_id)] = video_file_id
        
        markup = types.InlineKeyboardMarkup()
        
        clean_url = WEB_URL.rstrip('/')
        unlock_link = f"{clean_url}/?id={msg_id}"
        
        btn = types.InlineKeyboardButton("🔒 Watch & Get Video", url=unlock_link)
        markup.add(btn)
        
        caption_text = (
            "🔥 අලුත්ම වීඩියෝවක් එකතු විය!\n\n"
            "🎬 Video 3\n\n"
            "👇 වීඩියෝව ලබා ගැනීමට පහත Button එක ඔබන්න:"
        )
        
        try:
            bot.send_photo(
                TARGET_GROUP_ID, 
                photo_file_id, 
                caption=caption_text, 
                reply_markup=markup
            )
            bot.send_message(user_id, "✅ සාර්ථකයි! පෝස්ට් එක පබ්ලික් ගෲප් එකට යවන ලදී.")
            del pending_videos[user_id]
        except Exception as e:
            bot.send_message(user_id, f"❌ දෝෂයක්: {e}")
    else:
        bot.send_message(user_id, "කරුණාකර පළමුව ප්‍රයිවට් ගෲප් එකට වීඩියෝවක් දමන්න.")

# 3. යූසර් වෙබ් අඩවියේ ඇඩ්ස් බලා එන විට වීඩියෝව ලබා දීම
@bot.message_handler(commands=['start'])
def handle_start(message):
    text = message.text
    if "get_" in text:
        try:
            msg_id = text.split("get_")[1]
            video_id = video_storage.get(msg_id)
            
            if video_id:
                bot.send_message(message.chat.id, "🎉 සියලු දැන්වීම් බැලීම සාර්ථකයි! මෙන්න ඔබ ඉල්ලූ සම්පූර්ණ වීඩියෝව:")
                bot.send_video(message.chat.id, video_id)
            else:
                bot.send_message(message.chat.id, "⚠️ කල් ඉකුත් වූ හෝ සොයාගත නොහැකි වීඩියෝවකි.")
        except Exception as e:
            bot.send_message(message.chat.id, "❌ දෝෂයක් ඇති විය. කරුණාකර නැවත උත්සාහ කරන්න.")
    else:
        bot.send_message(
            message.chat.id, 
            "👋 සාදරයෙන් පිළිගනිමු!\nපබ්ලික් ගෲප් එකේ ඇති වීඩියෝ ලින්ක් එක හරහා දැන්වීම් නරඹා මෙහි පැමිණීමෙන් ඔබට අවශ්‍ය වීඩියෝ ලබාගත හැක."
        )

if __name__ == '__main__':
    print("Telegram Bot is running successfully...")
    bot.infinity_polling()
