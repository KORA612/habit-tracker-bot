import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from inputHandler import InputHandler
from database import DatabaseHandler


# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize handlers
db = DatabaseHandler()
input_handler = InputHandler()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user

    # Create/get user in database
    await db.create_user(
        telegram_id=user.id,
        username=user.username or user.first_name
    )

    welcome_message = (
        f"👋 Hi {user.first_name}!\n\n"
        "I'm your Daily Habit Tracker bot. I can help you track your daily activities "
        "and build better habits.\n\n"
        "Here are my main commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show available commands\n"
        "/track - Start tracking your day\n"
        "/stats - View your statistics\n\n"
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
        "For example: 'I woke up at 6:30, had a great breakfast until 7:15, then read for 45 minutes'"
    )
    await update.message.reply_text(track_message)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages."""
    try:
        # Download voice message
        file = await context.bot.get_file(update.message.voice.file_id)
        await file.download_to_drive('voice_message.ogg')

        # Process voice message
        activities = await input_handler.handle_voice_message('voice_message.ogg')

        # Log activities to database
        for activity in activities:
            await db.log_activity(
                user_id=update.effective_user.id,
                activity=activity.activity,
                timestamp=activity.time,
                duration=activity.duration,
                sentiment=activity.sentiment
            )

        # Format and send response
        response = input_handler.format_activities_for_display(activities)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Sorry, there was an error processing your message: {str(e)}")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    try:
        user_stats = await db.get_user_stats(update.effective_user.id)
        recent_activities = await db.get_user_activities(
            user_id=update.effective_user.id,
            limit=5
        )

        stats_message = (
            "📊 Your Stats:\n\n"
            f"Total Activities: {user_stats['total_activities']}\n"
            f"Current Streak: {user_stats['streak']} days\n"
            f"Total Duration: {user_stats['total_duration']} minutes\n\n"
            "🕒 Recent Activities:\n"
        )

        for activity in recent_activities:
            stats_message += f"• {activity['timestamp']}: {activity['activity']}\n"

        await update.message.reply_text(stats_message)

    except Exception as e:
        await update.message.reply_text("Sorry, there was an error retrieving your stats.")


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
