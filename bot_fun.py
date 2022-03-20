# Bot's functionality is here

# All the necessary packages
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import threading

from hidden import get_token # Token getter function

# Implement hidden token
updater = Updater(get_token(), use_context=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hi, I'm a news getter bot!\nCheck /help for available commands.")

def help(update: Update, context: CallbackContext):
    update.message.reply_text("Commands:\n/check - runs a check on news website\n/stop - stops the bot")

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry, you say what?")

def unknown_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry, not a valid command. Try /help to see all commands.")

def shutdown():
    updater.stop()
    updater.is_idle = False

def stop(update: Update, context: CallbackContext):
    threading.Thread(target=shutdown).start()

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('stop', stop))

# Filter out unknown commands
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_cmd))
# Filter out unknown messages
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

# Running the bot
updater.start_polling()
