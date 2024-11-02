# Daily Habit Tracker Bot 🤖

A Telegram bot that helps users track their daily activities and build better habits through voice messages and text interactions. The bot uses OpenAI's GPT-4 and Whisper API to process natural language inputs and provide structured activity tracking.

## Features ✨

- **Voice Message Processing**: Record your daily activities through voice messages
- **Natural Language Understanding**: Describes activities in your own words
- **Sentiment Analysis**: Automatically detects the mood/sentiment of activities
- **Activity Timeline**: Visual representation of your daily activities
- **Duration Tracking**: Automatically calculates activity durations
- **Statistics**: Track your progress and maintain streaks

## Prerequisites 📋

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- MongoDB Database

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/habit-tracker-bot.git
cd habit-tracker-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your credentials:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_MongoDB_database_url
```

## Usage 💡

1. Start the bot:
```bash
python bot.py
```

2. In Telegram, start a conversation with your bot and use these commands:
- `/start` - Initialize the bot and see welcome message
- `/help` - View available commands
- `/track` - Start tracking your activities
- `/stats` - View your activity statistics

3. Send voice messages describing your daily activities:
```
"I woke up at 6:30, had a great breakfast until 7:15, then read for 45 minutes"
```

## Project Structure 📁

```
habit-tracker-bot/
├── bot.py              # Main bot implementation
├── inputHandler.py     # Voice and text processing logic
├── database.py        # Database operations
├── requirements.txt   # Project dependencies
└── .env              # Environment variables
```

## Dependencies 📦

- python-telegram-bot
- openai
- python-dotenv
- pymongo

## How It Works 🛠️

1. **Voice Input Processing**:
   - User sends voice message
   - Bot converts speech to text using OpenAI Whisper
   - Text is processed to extract activities and timing

2. **Activity Extraction**:
   - Uses GPT-4 to understand natural language
   - Extracts time, duration, and sentiment
   - Structures data for storage

3. **Data Storage**:
   - Activities stored in MongoDB
   - Tracks user progress and streaks
   - Maintains historical data

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- OpenAI for GPT-4 and Whisper API
- Telegram Bot API
- All contributors and users of the bot

## Support 💬

For support, email `radmehrkooshan@gmail.com` or create an issue in the repository.

---
Good Luck!