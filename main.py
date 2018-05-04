from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          RegexHandler, ConversationHandler)
import requests
import logging
import json
import os
import sys


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -\
 %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

user = {"chat_id": None, "dev_ip": None}
ADDRESS = range(1)


# TG Command Handlers

def start(bot, update):
    """/start handler."""

    user["chat_id"] = update.message.chat.id
    update.message.reply_text(
        'Hello! Please enter IP address of the device in format {IP}:{PORT}.')
    return ADDRESS


def address(bot, update):
    """Add device address. Sync device with TG."""

    user["dev_ip"] = update.message.text
    logger.info("Device address of %s: %s", update.message.chat.id,
                update.message.text)

    if user["dev_ip"] is not None:
        send_credentials(user["dev_ip"])

    update.message.reply_text(("Address has been added."
                              " Use /ping to check if it's available."))


def help(bot, update):
    """/help handler."""

    update.message.reply_text(("List of available commands:\n"
                              "/register - register a device.\n"
                              "/ping - check if device is available.\n"
                              "/sentry - start survaillance module.\n"
                              ))


def sentry(bot, update):
    """/sentry handler."""

    if user["dev_ip"] is not None:
        reply = execute_command(user["dev_ip"], command="sentry")
    else:
        reply = "You have not set up device IP."
    update.message.reply_text(reply)


def ping(bot, update):
    """/ping handler."""

    reply = ""

    if user["dev_ip"] is not None:
        addr = "http://" + user["dev_ip"]
        try:
            r = requests.get(addr)
            if r.status_code == 200:
                reply = "Device is responding."
        except requests.exceptions.Timeout:
            reply = "Connection has been timed out!"
        except requests.exceptions.ConnectionError:
            reply = "Connection error!"
        except requests.exceptions.HTTPError:
            reply = "HTTP Error!"
        finally:
            update.message.reply_text(reply)
    else:
        reply = "You have not entered device IP."

        update.message.reply_text(reply)


def register(bot, update):
    "/register handler."

    update.message.reply_text("Enter your devices IP address.")
    return ADDRESS


def cancel(bot, update):
    """Stop conversation."""

    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("Stopping...")
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors."""

    logger.warning("Update '%s' caused error '%s'", update, error)



# Internal logic

def execute_command(address, **kwargs):
    """Execute command on remote device."""
    payload = kwargs.get('payload')
    if payload is None:
        payload = {'command': kwargs.get('command')}

    address = "http://" + address

    r = requests.post(address, data=json.dumps(payload))
    if r.status_code == 200:
        return "Command {} has been executed.".format(kwargs.get('command'))
    else:
        logger.warning("Could not send command to device. Error code: %s",
                       r.status_code)
        return "Could not execute command {}. Error code:{}".format(
            kwargs.get('command'), r.status_code)


def send_credentials(address):
    payload = {'command': 'creds',
               'api': os.getenv("TG_TOKEN"),
               'chat_id': str(user["chat_id"])}

    execute_command(address, payload=payload)


def main():
    # Create the EventHandler

    try:
        updater = Updater(os.getenv("TG_TOKEN", None))
    except ValueError:
        logger.fatal("Could not get Telegram token! Exiting...")
        sys.exit(1)

    # Create the dispatcher
    dp = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states = {
            ADDRESS:
            [RegexHandler('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$',
                          address)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Register all commands and their handlers
    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("sentry", sentry))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("register", register))

    # Log Errors
    dp.add_error_handler(error)

    logger.info("Starting Telegram Bot...")
    updater.start_polling()

    # Safe termination
    updater.idle()


if __name__ == "__main__":
    main()

