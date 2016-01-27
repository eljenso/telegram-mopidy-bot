#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
"""

import telegram
import logging
import configparser
import re
import subprocess
from os import path

import lib.mopidy as mopidy


configpath = 'config.txt'

botToken = ''
allowedChats = []
host = ''


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def loadConfig():
    global botToken
    global allowedChats
    global host
    config = configparser.RawConfigParser()
    if path.exists(configpath)==False:
        logger.error('"%s" does not exist.' % (configpath))
        return
    config.read(configpath)
    botToken = config.get('main', 'botToken')
    try:
        host = config.get('main', 'host')
    except Exception as e:
        host = subprocess.check_output("ip route show | awk '/default/ {print $3}'", shell=True).decode().replace("\n", ":6680")

    chats = config.items('allowedChats')
    for chat in chats:
        try:
            allowedChats.append(int(chat[1]))
        except ValueError as e:
            logger.error('Chat IDs should only be integers.')
            raise


def spotifyLinkHandler(bot, update):
    if not update.message.chat_id in allowedChats:
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but you are not allowed to change the music. :(")
    else:
        link = update.message.text
        logger.info(link)

        track_pattern = '/track/'
        album_pattern = '/album/'

        link_split = track_pattern.split(link)
        logger.info(link_split)
        if track_pattern in link:
            pattern = re.compile(track_pattern)
            split = pattern.split(link)
            mopidy.queue(host, 'spotify:track:%s' % (split[1]))
            bot.sendMessage(chat_id=update.message.chat_id, text="Great, playing the song for you.")
        elif album_pattern in link:
            pattern = re.compile(album_pattern)
            split = pattern.split(link)
            mopidy.queue(host, 'spotify:album:%s' % (split[1]))
            bot.sendMessage(chat_id=update.message.chat_id, text="Great, playing the album for you.")
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text="Please post a track link.")



# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help! Your ID is %s' % (update.message.chat_id))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def main():
    # Load config
    loadConfig()

    # Create the EventHandler and pass it your bot's token.
    try:
        updater = telegram.Updater(token=botToken)
    except telegram.error.TelegramError as e:
        logger.error('Could not init telegram bot. Is the bot token missing in the config?')
        raise


    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)
    dp.addUnknownTelegramCommandHandler(unknown)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramRegexHandler("^http[s]?://.*spotify\.com", spotifyLinkHandler)

    # log all errors
    dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
