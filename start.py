from telegram.ext.updater import Updater
from telegram.update import Update
from telegram import ParseMode

from news_re import download_image
from extract import publish, get_news
from hidden import get_token, get_chat_id

import time, datetime

# Create a bot with given token
updater = Updater(get_token(), use_context=True)


# Functions to prepare message for posting
def prepare_symbols(string):

    string = string.replace("-", "\-")
    string = string.replace(".", "\.")
    string = string.replace("!", "\!")
    string = string.replace("'", "\\'")
    string = string.replace('"', '\\"')
    string = string.replace("|", "\|")
    string = string.replace("(", "\(")
    string = string.replace(")", "\)")
    string = string.replace("&ndash;", "\-")
    string = string.replace("&mdash;", "\-")
    string = string.replace("&amp;", "\&")
    string = string.replace("<i>", "_")
    string = string.replace("</i>", "_")
    string = string.replace("<em>", "")
    string = string.replace("</em>", "")
    string = string.replace("&#x27;", "\\'")
    string = string.replace("+", "\+")
    string = string.replace(">", "\>")
    string = string.replace("<", "\<")
    string = string.replace("<!-- -->", "")

    return string

def construct_msg(title, synopsis, date_time, website, link):


    title = prepare_symbols(title)
    synopsis = prepare_symbols(synopsis)
    date_time = prepare_symbols(date_time)
    website = prepare_symbols(website)
    link = prepare_symbols(link)

    msg = f"*{title}*\n\n_{synopsis}\n\n{date_time}\n[{website}]({link})_"

    return msg


try:
    while True:
        arts = get_news()
        count = 0

        if len(arts) != 0:

            for i in range(len(arts)):
                
                # send a message in chat
                msg = construct_msg(title=arts[i][0], synopsis=arts[i][4], date_time=arts[i][5], website=arts[i][1], link=arts[i][2] + '/')
                img_path = download_image(arts[i][3])

                # update.message.reply_photo(photo=open(img_path, 'rb'), caption=msg, parse_mode=ParseMode.MARKDOWN_V2)
                try:   
                    updater.dispatcher.bot.send_photo(chat_id=get_chat_id(), photo=open(img_path, 'rb'), caption=msg, parse_mode=ParseMode.MARKDOWN_V2)
                except:
                    print('ERROR')
                    print('chat_id:', get_chat_id(), 'img_path:', img_path, 'msg:', msg)
                    break
                    
                publish(arts[i][0])
                count += 1
                time.sleep(5)

            print('Finished posting', count, 'new articles.')
        else:
            print('No new articles gotten.')

        # Waiting for next iteration after trying to post new articles
        curr_time = datetime.datetime.now()
        print(curr_time, 'Waiting for 20 mins until next check...')
        time.sleep(1200)

except KeyboardInterrupt:
    print('Interrupted!')
    