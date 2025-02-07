import os
import requests
import json
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def start(update, context):
    update.message.reply_text('Welcome to May Day Movement Bot! Send me updates to post to the website.')

def post_to_github(content):
    # GitHub repository details
    owner = "NoCoMozi"
    repo = "MayDayMovement"
    
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
    
    # Make the request
    response = requests.post(url, headers=headers, data=json.dumps({
        "event_type": event_type,
        "client_payload": client_payload
    }))
    
    return response.status_code == 204

def handle_message(update, context):
    content = update.message.text
    try:
        if post_to_github(content):
            update.message.reply_text("✅ Update posted successfully! The website will be updated shortly.")
        else:
            update.message.reply_text("❌ Error posting update. Please try again later.")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    # Get tokens from environment variables
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        telegram_token = input("Enter your Telegram bot token: ")
    
    # Create the Updater and pass it your bot's token
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()
    print("Bot is running! Send messages to your bot on Telegram.")
    print("Press Ctrl+C to stop.")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
