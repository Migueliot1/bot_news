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
