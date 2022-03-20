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
from news_re import get_data # Function which adds news articles to the table
from extract import get_news # Function which retrieves a list full of data from the table

arts = list() # List containing news articles

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

def check_for_news(update: Update, context: CallbackContext):
    get_data()
    update.message.reply_text(
        "Look up succesful. Use /get to see if there are any news.")

# not finished
def post_arts(update: Update, context: CallbackContext):
    arts = get_news()
    if len(arts) == 0:
        update.message.reply_text('No news *shrug*')
    for i in range(len(arts)):
        # send a message in chat
        update.message.reply_text(arts[i])

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('stop', stop))
updater.dispatcher.add_handler(CommandHandler('check', check_for_news))
# updater.dispatcher.add_handler(CommandHandler('post', post_arts))

# Filter out unknown commands
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_cmd))
# Filter out unknown messages
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

# Running the bot
updater.start_polling()
