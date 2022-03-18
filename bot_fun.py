# Bot's functionality is here

# All the necessary packages
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

# Token getter function
from hidden import get_token

# Implement hidden token
updater = Updater(get_token(), use_context=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hi, I'm a news getter bot!")

def help(update: Update, context: CallbackContext):
    update.message.reply_txt(
        "Here is going to be a help message.")

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_txt(
        "Sorry, you say what?")

def unknown_cmd(update: Update, context: CallbackContext):
    update.message.reply_txt(
        "Sorry, not a valid command. Try /help to see all commands.")


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
# Filter out unknown commands
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_cmd))
# Filter out unknown messages
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

# Running the bot
updater.start_polling()
