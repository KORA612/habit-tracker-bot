import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Hi {user.first_name}!\n\n"
        "I'm your Daily Habit Tracker bot. I can help you track your daily activities "
        "and build better habits.\n\n"
        "Here are my main commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show available commands\n"
        "/track - Start tracking your day\n\n"
        "You can also send me voice messages describing your day, "
        "and I'll help you track your activities!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "📋 Available Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/track - Start tracking your day\n"
        "\nYou can also:\n"
        "🎤 Send voice messages about your day\n"
        "📊 View your progress (coming soon)\n"
        "⏰ Set reminders (coming soon)"
    )
    await update.message.reply_text(help_text)

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /track command."""
    track_message = (
        "🎯 Let's track your day!\n\n"
        "You can either:\n"
        "1. Send me a voice message describing your activities\n"
        "2. Type out what you've done today\n\n"
        "For example: 'I woke up at 6, had breakfast at 7, and worked until noon'"
    )
    await update.message.reply_text(track_message)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages."""
    await update.message.reply_text(
        "🎤 I received your voice message! (Voice processing coming soon)"
    )

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("track", track))
    
    # Add voice message handler
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Add error handler
    application.add_error_handler(error)

    # Start the Bot
    print('Bot is starting...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()