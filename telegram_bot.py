import os
import requests
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set up HTTP session with retries
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
http = requests.Session()
http.mount("https://", HTTPAdapter(max_retries=retry_strategy))

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to May Day Movement Bot! Send me updates to post to the website.')

def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        message_text = update.message.text
        chat_id = update.message.chat_id
        
        # Create the payload for the workflow
        payload = {
            'event_type': 'telegram-update',
            'client_payload': {
                'content': message_text,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        }
        
        # Trigger the workflow via GitHub API
        headers = {
            'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.post(
            'https://api.github.com/repos/NoCoMozi/MayDayMovement-clean/dispatches',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 204:
            update.message.reply_text("✅ Update received! The website will be updated shortly.")
        else:
            update.message.reply_text(f"❌ Error: Could not process update. Status code: {response.status_code}")
            logger.error(f"GitHub API error: {response.text}")
            
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        update.message.reply_text("❌ Sorry, there was an error processing your update. Please try again later.")

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    # Create the Updater
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()
    logger.info("Bot is running! Send messages to your bot on Telegram.")
    logger.info("Press Ctrl+C to stop.")

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
