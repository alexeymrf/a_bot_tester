# a_bot Telegram Bot Tester

Automated testing tool for the a_bot Telegram bot using Telethon.

## Features

- 🤖 Automated Telegram bot testing via user account
- 📋 Test all bot commands (`/start`, `/help`, `/spreads`, `/alerts`, `/newalert`, `/settings`)
- 🔘 Interactive button/callback testing
- 📊 Comprehensive test reports
- ⏱️ Response time measurement
- 🔄 Conversation flow testing

## Requirements

- Python 3.11+
- Telegram API credentials (api_id and api_hash)
- User account (not bot)

## Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy `api_id` and `api_hash`

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. First Run (Authentication)

```bash
python -m src.auth
```

This will:
- Prompt for your phone number
- Send a code to your Telegram
- Create a session file for future runs

## Usage

### Run All Tests

```bash
python -m src.main --bot-username your_bot_username
```

### Run Specific Tests

```bash
# Test only commands
python -m src.main --bot-username your_bot_username --test commands

# Test only buttons/callbacks
python -m src.main --bot-username your_bot_username --test callbacks

# Test conversation flows
python -m src.main --bot-username your_bot_username --test flows
```

### Interactive Mode

```bash
python -m src.interactive --bot-username your_bot_username
```

## Test Scenarios

### Commands
- `/start` - Registration and welcome message
- `/help` - Help information
- `/spreads` - Funding rate spreads display
- `/alerts` - User alerts list
- `/newalert` - Alert creation flow
- `/settings` - User settings
- `/menu` - Main menu display

### Callback Buttons
- Menu navigation
- Pagination (spreads, alerts)
- Alert management (view, toggle, delete)
- Settings modification
- Language switching

### Conversation Flows
- Complete alert creation
- Settings modification
- Full user journey

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_API_ID` | Telegram API ID | Yes |
| `TELEGRAM_API_HASH` | Telegram API Hash | Yes |
| `TELEGRAM_PHONE` | Your phone number | Yes |
| `TARGET_BOT_USERNAME` | Bot username to test | Yes |
| `SESSION_NAME` | Session file name | No (default: `tester`) |
| `LOG_LEVEL` | Logging level | No (default: `INFO`) |

## Project Structure

```
a_bot_tester/
├── src/
│   ├── __init__.py
│   ├── main.py           # Main entry point
│   ├── auth.py           # Authentication helper
│   ├── interactive.py    # Interactive testing mode
│   ├── config.py         # Configuration
│   ├── client.py         # Telethon client wrapper
│   ├── tester.py         # Test orchestrator
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── base.py       # Base test class
│   │   ├── commands.py   # Command tests
│   │   ├── callbacks.py  # Callback tests
│   │   └── flows.py      # Flow tests
│   └── utils/
│       ├── __init__.py
│       ├── logging.py    # Logging utilities
│       └── report.py     # Test reporting
├── tests/                # pytest tests
├── .env.example
├── pyproject.toml
└── README.md
```

## Security Notes

⚠️ **Important**: This tool uses your personal Telegram account, not a bot.

- Never share your `.session` files
- Keep your API credentials secret
- Don't run automated tests too frequently to avoid rate limits
- This is for testing YOUR bots only

## License

MIT
