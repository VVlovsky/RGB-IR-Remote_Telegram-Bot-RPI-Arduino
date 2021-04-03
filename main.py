
import logging
import bluetooth
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

CAL, CON = "CAL", "CON"
OFF, ON = 'OFF', 'ON'
sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

with open("config.json", "rb") as read_file:
    TOKEN = json.load(read_file)['TOKEN']


def start(update: Update, _: CallbackContext) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=ON),
            InlineKeyboardButton("No", callback_data=OFF),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Is light enabled now?", reply_markup=reply_markup)

    return CON


def start_over(update: Update, _: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""

    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=ON),
            InlineKeyboardButton("No", callback_data=OFF),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Is light enabled now? 💡", reply_markup=reply_markup)
    return CON


def control_panel(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    sock.send('e')
    keyboard = [
        [
            InlineKeyboardButton('+', callback_data='+'),
            InlineKeyboardButton('-', callback_data='-'),
            InlineKeyboardButton("OFF", callback_data='OFF'),
        ],
        [
            InlineKeyboardButton("❤️", callback_data='r'),
            InlineKeyboardButton("💚", callback_data='g'),
            InlineKeyboardButton("💙", callback_data='b'),
            InlineKeyboardButton("🤍", callback_data='w'),
        ],
        [
            InlineKeyboardButton("🟠", callback_data='0'),
            InlineKeyboardButton("🟢", callback_data='1'),
            InlineKeyboardButton("🔵", callback_data='2'),
            InlineKeyboardButton("FLASH", callback_data='<'),
        ],
        [
            InlineKeyboardButton("🏮", callback_data='3'),
            InlineKeyboardButton("💧", callback_data='4'),
            InlineKeyboardButton("☂️", callback_data='5'),
            InlineKeyboardButton("STROBE", callback_data='='),
        ],[
            InlineKeyboardButton("🌅", callback_data='6'),
            InlineKeyboardButton("💎", callback_data='7'),
            InlineKeyboardButton("🎀", callback_data='8'),
            InlineKeyboardButton("FADE", callback_data='>'),
        ],[
            InlineKeyboardButton("⚱️", callback_data='9'),
            InlineKeyboardButton("🐳", callback_data=':'),
            InlineKeyboardButton("🌸", callback_data=';'),
            InlineKeyboardButton("SMOOTH", callback_data='?'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="CONTROL PANEL 💡", reply_markup=reply_markup
    )
    return CON


def control_disabled(update: Update, _: CallbackContext) -> str:
    sock.send('d')
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Enable 💡", callback_data=ON),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="The Light is Disabled", reply_markup=reply_markup
    )
    return CON


def button(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    logger.info(f'sended {query.data}')
    sock.send(query.data)
    return CON


def main() -> None:

    searching = True
    while searching:
        nearby_devices = bluetooth.discover_devices(duration=15)
        num = 0
        for i in nearby_devices:
            print(bluetooth.lookup_name( i ))
            if bluetooth.lookup_name( i ) == "JDY-31-SPP":
                selection = num
                break
            num = num + 1
        try:
            if selection >= 0:
                searching = False;
        except Exception as e:
            print(e)
            print('try again')

    print(bluetooth.lookup_name(nearby_devices[selection]))
    bd_addr = nearby_devices[selection]
    port = 1
    sock.connect((bd_addr, port))
    
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CON: [
                CallbackQueryHandler(control_panel, pattern='^' + ON + '$'),
                CallbackQueryHandler(control_disabled, pattern='^' + OFF + '$'),
                CallbackQueryHandler(button)

            ],
            CAL: [
                CallbackQueryHandler(start_over, pattern='^' + ON + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
