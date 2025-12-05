# A_Bot Tester

Automated Telegram bot tester using Telethon to test a_bot commands.

## Setup

1. Get your Telegram API credentials from https://my.telegram.org/apps
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies: `pip install -e .`
4. Run the tester: `python tester.py`

## Usage

```bash
# Test all commands
python tester.py --all

# Test specific command
python tester.py --command /start

# Interactive mode
python tester.py --interactive
```

## Required Environment Variables

- `TELEGRAM_API_ID` - Your Telegram API ID
- `TELEGRAM_API_HASH` - Your Telegram API Hash
- `BOT_USERNAME` - Username of the bot to test (e.g., @your_funding_bot)
