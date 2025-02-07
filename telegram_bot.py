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
        logger.info(f"Received message: {message_text}")
        
        # Create the payload for the workflow
        payload = {
            'event_type': 'telegram-update',
            'client_payload': {
                'content': message_text,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        }
        
        logger.info("Sending request to GitHub API...")
        
        # Trigger the workflow via GitHub API with retries
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            logger.error("GITHUB_TOKEN environment variable is not set!")
            update.message.reply_text("❌ Error: GitHub token not configured.")
            return
            
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to post to GitHub API (attempt {retry_count + 1}/{max_retries})")
                response = http.post(
                    'https://api.github.com/repos/NoCoMozi/MayDayMovement-clean/dispatches',
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                logger.info(f"GitHub API response status code: {response.status_code}")
                logger.info(f"GitHub API response headers: {response.headers}")
                logger.info(f"GitHub API response text: {response.text}")
                
                if response.status_code == 204:
                    update.message.reply_text("✅ Update received! The website will be updated shortly.")
                    logger.info("Successfully triggered GitHub workflow")
                    return
                else:
                    logger.error(f"GitHub API error response: {response.text}")
                    retry_count += 1
                    if retry_count == max_retries:
                        error_msg = f"❌ Error: Could not process update. Status code: {response.status_code}, Response: {response.text}"
                        update.message.reply_text(error_msg)
                    else:
                        logger.info(f"Retrying... Attempt {retry_count + 1}/{max_retries}")
                        time.sleep(1)
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                retry_count += 1
                if retry_count == max_retries:
                    update.message.reply_text("❌ Connection error. Please try again later.")
                    break
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        update.message.reply_text("❌ Sorry, there was an error processing your update. Please try again later.")

def handle_photo(update: Update, context: CallbackContext) -> None:
    """Handle photo messages."""
    try:
        update.message.reply_text("❌ Sorry, I can only process text messages at the moment. Please send your update as text.")
    except Exception as e:
        logger.error(f"Error handling photo: {str(e)}")
        update.message.reply_text("❌ Error processing your message. Please try sending text only.")

def handle_document(update: Update, context: CallbackContext) -> None:
    """Handle document messages."""
    try:
        update.message.reply_text("❌ Sorry, I can only process text messages at the moment. Please send your update as text.")
    except Exception as e:
        logger.error(f"Error handling document: {str(e)}")
        update.message.reply_text("❌ Error processing your message. Please try sending text only.")

def handle_other(update: Update, context: CallbackContext) -> None:
    """Handle other types of messages."""
    try:
        update.message.reply_text("❌ Sorry, I can only process text messages at the moment. Please send your update as text.")
    except Exception as e:
        logger.error(f"Error handling other message type: {str(e)}")
        update.message.reply_text("❌ Error processing your message. Please try sending text only.")

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    while True:  # Add infinite retry loop
        try:
            # Create the Updater
            token = os.getenv('TELEGRAM_TOKEN')
            if not token:
                logger.error("TELEGRAM_TOKEN environment variable is not set!")
                return
                
            logger.info("Starting bot...")
            
            # Create the updater with minimal settings
            updater = Updater(token, use_context=True)

            # Get the dispatcher to register handlers
            dp = updater.dispatcher

            # Add handlers
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            dp.add_handler(MessageHandler(Filters.photo, handle_photo))
            dp.add_handler(MessageHandler(Filters.document, handle_document))
            dp.add_handler(MessageHandler(~Filters.text & ~Filters.photo & ~Filters.document, handle_other))
            dp.add_error_handler(error_handler)

            # Start the Bot with graceful shutdown
            updater.start_polling(drop_pending_updates=True, timeout=30)
            logger.info("Bot is running! Send messages to your bot on Telegram.")
            logger.info("Press Ctrl+C to stop.")

            # Run the bot until you press Ctrl-C or get a stop signal
            updater.idle()
            
            # If we get here normally (through Ctrl+C), break the retry loop
            break
            
        except Exception as e:
            logger.error(f"Fatal error in main loop: {str(e)}")
            logger.info("Waiting 10 seconds before restarting...")
            time.sleep(10)  # Wait before retrying
            continue

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user. Exiting...")
    except Exception as e:
        logger.error(f"Unrecoverable error: {str(e)}")
