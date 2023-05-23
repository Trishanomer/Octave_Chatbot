import importlib
import time
import re
from sys import argv
from typing import Optional

from AaruRobot import (
    ALLOW_EXCL,
    OWNER_USERNAME,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from AaruRobot.modules import ALL_MODULES
from AaruRobot.modules.helper_funcs.chat_status import is_user_admin
from AaruRobot.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
*ʜᴇʏ,\n ᴛʜɪs ɪs 𝐀𝐀𝐑𝐔🇽 𝐑𝐎𝐁𝐎𝐓 * [!](https://telegra.ph/file/113a384afe93aed25d2df.jpg)\n\n *ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀꜰᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴏꜰ ᴛᴇʟᴇɢʀᴀᴍ.\n  ɪ ʜᴀᴠᴇ ᴀᴡᴇsᴏᴍᴇ ꜰᴇᴀᴛᴜʀᴇs ᴀɴᴅ ɴᴏ ᴏɴᴇ ᴄᴀɴ ʙᴇᴀᴛ ᴍᴇ. ɪ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴡɪᴛʜ ꜰᴜʟʟʏ ᴀᴜᴛᴏᴍᴀᴛɪᴄ ꜰᴇᴀᴛᴜʀᴇꜱ.*

ʀᴇᴀᴅ ᴛʜᴇ ɪɴᴠᴏɪᴄᴇ ᴄᴀʀᴇꜰᴜʟʟʏ ᴀɴᴅ ᴍᴀɪɴᴛᴀɪɴ ᴛʜᴇ ᴘᴀʏᴍᴇɴᴛ ꜰᴏʀ ʀᴇɢᴜʟᴀʀ ꜱᴇʀᴠɪᴄᴇꜱ.
 
ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴋɴᴏᴡ ᴀʙᴏᴜᴛ ᴛʜᴇ ꜰᴇᴀᴛᴜʀᴇꜱ ᴀɴᴅ ᴡᴀɴᴛ ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ ᴏʀ ʀᴇɴᴛ ᴍᴇ, ᴛʜᴇɴ ᴘʟᴇᴀꜱᴇ ᴍᴇꜱꜱᴀɢᴇ  ᴍʏ [ʙᴏꜱꜱ](https://t.me/{OWNER_USERNAME})**

**Pʀᴏɢʀᴀᴍᴍᴇʀ**: [🎩sᴜʟʟɪᴇᴍᴀɴᴛʀʏ🎩](https://t.me/sullicodes)

"""

buttons = [
    [
        InlineKeyboardButton(text="ᴍʏ ɪɴᴠᴏɪᴄᴇ", url=f"{DONATION_LINK}"),
    ],
    [
        InlineKeyboardButton(
            text="💡ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs💡", callback_data="help_data"
        ),
    ],
]

AaruRobot_IMG = "https://telegra.ph/file/113a384afe93aed25d2df.jpg"

HELP_STRINGS = """<b>✪ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>

▶️  /start  →  ᴄʀᴇᴀᴛᴇꜱ ᴀ ʙᴇᴀᴜᴛɪꜰᴜʟ ʜᴏᴍᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴀʀᴏᴜꜱᴇ ɪɴᴛᴇʀᴇꜱᴛ

▶️  /help  →  ʏᴏᴜʀ ᴍᴀɪɴ ᴄᴏᴍᴘᴀɴɪᴏɴ ɪɴ ʜᴀɴᴅʟɪɴɢ ᴀʀᴏᴜɴᴅ ᴡɪᴛʜ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅꜱ

▶️  /donate  →  ᴅᴏɴᴀᴛᴇ ᴜꜱ ᴛᴏ ᴀꜱꜱɪꜱᴛ ɪɴ ᴋᴇᴇᴘɪɴɢ ᴜꜱ ʟɪᴠᴇ

▶️  /ping  →  ᴄʜᴇᴄᴋ ᴛʜᴇ ʙᴏᴛ'ꜱ ʟᴀᴛᴇɴᴄʏ

▶️  /about  →  ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ

▶️  /cancel  →  ᴄᴀɴᴄᴇʟ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ
"""

DONATE_STRING = """🎗 <b>ᴅᴏɴᴀᴛᴇ</b> 🎗

ʏᴏᴜ ᴄᴀɴ ᴅᴏɴᴀᴛᴇ ᴛᴏ ᴜꜱ ᴛᴏ ꜱᴜᴘᴘᴏʀᴛ ᴏᴜʀ ᴘʀᴏᴊᴇᴄᴛ. ʏᴏᴜʀ ᴋɪɴᴅɴᴇꜱꜱ ᴡɪʟʟ ᴇɴᴄᴏᴜʀᴀɢᴇ ᴜꜱ ᴛᴏ ᴅᴏ ᴍᴏʀᴇ ᴅᴇᴠᴇʟᴏᴘᴍᴇɴᴛ.

ᴘʟᴇᴀꜱᴇ ᴛᴀᴘ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ғᴏʀ ᴅᴏɴᴀᴛɪᴏɴ.

ᴛʜᴀɴᴋ ʏᴏᴜ ɪɴ ᴀᴅᴠᴀɴᴄᴇ ғᴏʀ ʏᴏᴜʀ ꜱᴜᴘᴘᴏʀᴛ!

"""

ABOUT_STRING = """📖 <b>ᴀʙᴏᴜᴛ</b> 📖

<code>𝐀𝐀𝐑𝐔🇽 𝐑𝐎𝐁𝐎𝐓</code> ɪꜱ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ [🎩sᴜʟʟɪᴇᴍᴀɴᴛʀʏ🎩](https://t.me/sullicodes) ᴜsɪɴɢ ᴛʜᴇ ᴛᴇʟᴇᴛʜᴏɴ ʟɪʙʀᴀʀʏ.

<code>𝐀𝐀𝐑𝐔🇽 𝐑𝐎𝐁𝐎𝐓</code> ʜᴀꜱ ᴀ ᴠᴀʀɪᴇᴛʏ ᴏꜰ ᴘᴏᴡᴇʀꜰᴜʟ ꜰᴇᴀᴛᴜʀᴇꜱ ꜱᴜᴄʜ ᴀꜱ:

▶️ <b>ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛɪᴠᴇ ᴄᴏᴍᴍᴀɴᴅꜱ</b> - ᴍᴀɴᴀɢᴇ ᴛʜᴇ ɢʀᴏᴜᴘ ᴇᴀꜱɪʟʏ ᴡɪᴛʜ ᴄᴏᴍᴍᴀɴᴅꜱ ꜰᴏʀ ᴋɪᴄᴋɪɴɢ, ʙᴀɴɴɪɴɢ, ᴍᴜᴛɪɴɢ, ᴇᴛᴄ.

▶️ <b>ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴀᴄᴛɪᴏɴꜱ</b> - ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ, ʀᴇꜱᴘᴏɴᴅ ᴛᴏ ʟɪɴᴋꜱ, ʙʟᴏᴄᴋ ꜱᴘᴀᴍ, ᴇᴛᴄ.

▶️ <b>ꜱᴇʟꜰ-ʀᴏʟᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b> - ᴀʟʟᴏᴡ ᴜꜱᴇʀꜱ ᴛᴏ ᴀᴅᴅ/ʀᴇᴍᴏᴠᴇ ᴛʜᴇᴍꜱᴇʟᴠᴇꜱ ꜰʀᴏᴍ ꜱᴘᴇᴄɪꜰɪᴄ ʀᴏʟᴇꜱ.

▶️ <b>ᴘᴏʟʟꜱ ᴀɴᴅ Q&ᴀ</b> - ᴄʀᴇᴀᴛᴇ ᴀɴᴅ ᴍᴀɴᴀɢᴇ ᴘᴏʟʟꜱ ᴀɴᴅ Q&ᴀ ꜱᴇꜱꜱɪᴏɴꜱ ᴡɪᴛʜɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.

▶️ <b>ᴀɴᴛɪ-ꜱᴘᴀᴍ ꜰɪʟᴛᴇʀ</b> - ᴅᴇꜰᴇɴᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ꜱᴘᴀᴍᴍᴇʀꜱ ᴡɪᴛʜ ᴛʜᴇ ᴀɴᴛɪ-ꜱᴘᴀᴍ ꜰɪʟᴛᴇʀ.

...ᴀɴᴅ ᴍᴀɴʏ ᴍᴏʀᴇ!

ꜱᴇɴᴅ ᴍᴇ ᴀ ᴍᴇꜱꜱᴀɢᴇ ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ <code>𝐀𝐀𝐑𝐔🇽 𝐑𝐎𝐁𝐎𝐓</code>!

"""

CANCEL_STRING = "🚫 <b>ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟᴇᴅ</b> 🚫"

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=START_STRING, parse_mode=ParseMode.HTML)

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_STRING, parse_mode=ParseMode.HTML)

def donate(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=DONATE_STRING, parse_mode=ParseMode.HTML)

def about(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=ABOUT_STRING, parse_mode=ParseMode.HTML)

def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=CANCEL_STRING, parse_mode=ParseMode.HTML)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Define the command handlers
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    donate_handler = CommandHandler('donate', donate)
    about_handler = CommandHandler('about', about)
    cancel_handler = CommandHandler('cancel', cancel)

    # Register the command handlers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(donate_handler)
    dispatcher.add_handler(about_handler)
    dispatcher.add_handler(cancel_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

# Run the main function
if __name__ == '__main__':
    main()
