import os
import requests
import json
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure requests to retry on connection errors
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

def start(update, context):
    update.message.reply_text('Welcome to May Day Movement Bot! Send me updates to post to the website.')

def post_to_github(content):
    # GitHub repository details
    owner = "NoCoMozi"
    repo = "MayDayMovement-clean"
    
    # Get GitHub token from environment
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GitHub token not found in environment variables")
    
    # Prepare the dispatch event data
    event_type = "telegram-update"
    client_payload = {
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # GitHub API endpoint for repository dispatch
    url = f"https://api.github.com/repos/{owner}/{repo}/dispatches"
    
    # Headers for authentication
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make the request with retry session
        response = http.post(url, headers=headers, json={
            "event_type": event_type,
            "client_payload": client_payload
        })
        
        if response.status_code == 204:
            logger.info("Successfully posted update to GitHub")
            return True
        else:
            logger.error(f"Failed to post update. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error posting to GitHub: {str(e)}")
        return False

def handle_message(update, context):
    content = update.message.text
    try:
        if post_to_github(content):
            update.message.reply_text("✅ Update posted successfully! The website will be updated shortly.")
        else:
            update.message.reply_text("❌ Error posting update. Please try again later.")
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        update.message.reply_text(f"❌ Error: {str(e)}")

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.message:
            update.message.reply_text("❌ An error occurred. Please try again later.")
    except:
        logger.error("Could not send error message to user")

def main():
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Get Telegram token from environment variable
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not telegram_token:
                raise ValueError("Telegram bot token not found in environment variables")
            
            # Create the Updater and pass it your bot's token
            updater = Updater(telegram_token, use_context=True)

            # Get the dispatcher to register handlers
            dp = updater.dispatcher

            # Add handlers
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
            dp.add_error_handler(error_handler)

            # Start the Bot
            updater.start_polling(drop_pending_updates=True)
            print("Bot is running! Send messages to your bot on Telegram.")
            print("Press Ctrl+C to stop.")
            
            # Run the bot until you press Ctrl-C
            updater.idle()
            break  # If we get here, the bot started successfully
            
        except Exception as e:
            logger.error(f"Error starting bot (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Could not start bot.")
                raise

if __name__ == '__main__':
    main()
