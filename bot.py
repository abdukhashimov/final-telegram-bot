# start of importing
import os
import logging
from emoji import emojize
from gettext import gettext as _
from gettext import translation

from telegram import InlineKeyboardButton, InlineKeyboardMarkup,\
    KeyboardButton, ReplyKeyboardMarkup

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)
# end of importing

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
# ###################################################################


# 4 availbale states
# 1 - language - when it is tarted
# 2 - options of services
# 3 - contact
# 4 - final - if user enters contact not shares
LANGUAGE, OPTIONS, CONTACT, FINAL = range(4)


# language options are stored directly in the memory
language = {}
keyboard_option = {}


# Helper functions with langauge and keyboard
def update_language(user_id, option):
    # print(user_id)
    global language
    if option in ['en', 'uz', 'ru']:
        language[str(user_id)] = option


def get_language(user_id):
    global language
    return language.get(str(user_id), None)


def update_keyboard(user_id, keyboard_):
    global keyboard_option
    keyboard_option[str(user_id)] = keyboard_


def get_keyboard(user_id):
    global keyboard_option
    return keyboard_option.get(str(user_id), None)
# end of the helper functions with keyboards and language

# install language globally


def return_translation_function(user_id):
    option = get_language(user_id)
    language_ = translation(option, localedir='locales',
                            languages=['ru', 'uz', 'en'])
    language_.install()
    _ = language_.gettext
    return _
# the function which is triggered when start command is given


def start_language(update, context):
    reply_keyboard = [['UZ', 'RU', 'EN']]
    # print(update.message.from_user.id)
    update.message.reply_text(
        "Iltimos, tilni tanlang\n"
        'Пожалуйста, выберите ваш язык\n'
        'Please, choose your language\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    return LANGUAGE


def get_list_of_services(user_id):
    _ = return_translation_function(user_id)
    return [
        _('Logo Design'),
        _('Web Development'),
        _('Mobile Development'),
        _('Telegram Bot'),
        _('SEO Optimization'),
        _('E-commerce'),
    ]


def confirm_language(update, context):
    global language
    text = update.message.text.lower()
    user = update.message.from_user

    try:
        update_language(user.id, text)
    except Exception as e:
        print('The language you chose is not available yet.')
        update.message.reply_text(
            _('Language you chose is not available yet.')
        )
        return LANGUAGE
    # print(get_language(user_id=user.id))
    _ = return_translation_function(user_id=user.id)
    update.message.reply_text(
        _('Your language: {}').format(get_language(user.id).title())
    )
    keyboard = []
    services = get_list_of_services(user.id)
    for index, service in enumerate(services):
        keyboard.append([InlineKeyboardButton(
            service, callback_data=str(index))])

    keyboard.append([InlineKeyboardButton(_('{} Done').format(
        emojize(':ok:', use_aliases=True)), callback_data='done')])

    update_keyboard(user.id, keyboard)

    r_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        _('Please choose one of our services'),
        reply_markup=r_markup
    )

    return OPTIONS

# helper functions


def change_text(text):
    checkbox = emojize(':white_check_mark:', use_aliases=True)
    if checkbox in text:
        return " ".join(text.split()[1:])
    return '{} {}'.format(checkbox, text)


def make_message_from_list(list_of_orders, user_id):
    _ = return_translation_function(user_id)
    message = _('Your orders so far')
    for element in list_of_orders:
        message += '\n' + element
    return message


def string_from_array(keyboard):
    array = []
    for button in keyboard:
        if "{}".format(emojize(':white_check_mark:', use_aliases=True)) in button[0].text:
            array.append(button[0].text)
    return array
# end of the helpher functions


def options(update, context):
    query = update.callback_query
    user_id = query.message.chat.id
    bot = context.bot
    keyboard = get_keyboard(user_id)
    _ = return_translation_function(user_id)

    if query.data == 'done':
        array = string_from_array(keyboard)

        if len(array) == 0:
            return OPTIONS
        text = make_message_from_list(array, user_id)

        bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
        )

        bot.send_message(
            chat_id='956620330',
            text="Possible Client\n{} : @{}\nOrders: \n{}".format(
                query.message.chat.first_name,
                query.message.chat.username,
                "\n".join(text.split('\n')[1:])
            )
        )

        # Next state going
        contact_keyboard = [
            KeyboardButton(text=_("Send My Contact"), request_contact=True),
            KeyboardButton(text=_("I have other number")),
        ]

        bot.send_message(
            chat_id=query.message.chat.id,
            text=_("Would you mind sharing your contact?"),
            reply_markup=ReplyKeyboardMarkup(
                [contact_keyboard], one_time_keyboard=True, resize_keyboard=True)
        )

        return CONTACT
    else:
        text = change_text(keyboard[int(query.data)][0].text)
        keyboard[int(query.data)][0].text = text
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=_('Please choose one of our services'),
            reply_markup=reply_markup
        )

    return OPTIONS


def contact_send(update, context):
    user_id = str(update.message.from_user.id)
    _ = return_translation_function(user_id)
    contact = update.message
    context.bot.send_message(
        chat_id='956620330',
        text='PHONE NUMBER: +'+(contact.contact.phone_number) +
        '\n------------------------\n'
    )
    update.message.reply_text(
        _("Thank you very much, we will contact you soon")
    )
    return ConversationHandler.END


def contact_get(update, context):
    user_id = update.message.from_user.id
    _ = return_translation_function(user_id)
    update.message.reply_text(
        "{}\n{}\n{}\n{}\n".format(_("Please then send me your contact"),
                                  _("Make sure it is in the form as follows"),
                                  _("+998 93 578 97 68"),
                                  _("Go ahead"))
    )
    return FINAL


def contact_request(update, context):
    user_id = str(update.message.from_user.id)
    _ = return_translation_function(user_id)
    contact = update.message.text
    context.bot.send_message(
        chat_id='956620330',
        text='PHONE NUMBER: ' + str(contact) + '\n------------------------\n'
    )
    update.message.reply_text(
        _("Thank you very much, we will contact you soon")
    )
    return ConversationHandler.END


def contact_wrong(update, context):
    user_id = update.message.from_user.id
    _ = return_translation_function(user_id)
    update.message.reply_text(
        "{}\n{}\n".format(_("Please make sure that your contact's pattern is as follows"),
                          _("+998 93 578 97 68"))
    )
    return FINAL


def error_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # 1017586683:AAH9YvHhXuIrWRiQkz0VdbY6zJEkMe23l9c
    TOKEN = '1017586683:AAH9YvHhXuIrWRiQkz0VdbY6zJEkMe23l9c'
    NAME = "telegram-bot-test-first"
    PORT = os.environ.get('PORT')
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_language)],
        states={
            LANGUAGE: [
                MessageHandler(Filters.regex(
                    '^(RU|EN|UZ)$'), confirm_language),
                MessageHandler(Filters.text, start_language)
            ],
            OPTIONS: [
                CallbackQueryHandler(options, pattern=r'[0-6]|^done$')
            ],
            CONTACT: [
                MessageHandler(Filters.contact, contact_send),
                MessageHandler(Filters.text, contact_get)
            ],
            FINAL: [
                MessageHandler(Filters.regex(
                    '^(\+998[\s]?\d{2}[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2})$'),
                    contact_request),
                MessageHandler(Filters.text, contact_wrong)
            ]
        },
        fallbacks=[CommandHandler('start', start_language)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error_handler)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    updater.idle()


if __name__ == "__main__":
    main()
