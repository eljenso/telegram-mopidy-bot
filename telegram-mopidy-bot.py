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
from os import path

import lib.mopidy as mopidy


configpath = 'config.txt'

botToken = ''
allowedChats = []
host = ''


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def readConfig():
    global botToken
    global allowedChats
    config = configparser.RawConfigParser()
    if path.exists(configpath)==False:
        logger.error('"%s" does not exist.' % (configpath))
        return
    config.read(configpath)
    botToken = config.get('main', 'botToken')
    host = config.get('main', 'host')
    chats = config.items('allowedChats')
    for chat in chats:
        try:
            allowedChats.append(int(chat[1]))
        except ValueError as e:
            logger.error('Chat IDs should only be integers.')
            raise


def spotifyLinkHandler(bot, update):
    link = update.message.text
    logger.info(link)
    pattern = re.compile('/track/')
    link_split = pattern.split(link)
    logger.info(link_split)
    if len(link_split) == 2:
        mopidy.queue(host, 'spotify:track:%s' % (link_split[1]))
        bot.sendMessage(chat_id=update.message.chat_id, text="Great, playing the song for you.")
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Please post a track link.")


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def message(bot, update):
    if update.message.chat_id in allowedChats:
        bot.sendMessage(update.message.chat_id, text=update.message.text)
    else:
        logger.warn('Received message from unauthorized chat ID %s' % (update.message.chat_id))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def main():
    # Load config
    readConfig()

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
