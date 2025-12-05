# A_Bot Tester

A Telethon-based automated testing bot for testing the `a_bot` Telegram bot.

## Features

- **Automated Command Testing**: Send commands to the bot and verify responses
- **Test Scenarios**: Define test scenarios in YAML format
- **Response Validation**: Validate bot responses against expected patterns
- **Test Reports**: Generate test execution reports
- **CI/CD Integration**: Can be integrated into CI/CD pipelines

## Prerequisites

1. **Telegram API Credentials**: You need to obtain `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org)
2. **Python 3.11+**
3. **The target bot must be running**

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd a_bot_tester

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
TARGET_BOT_USERNAME=your_bot_username
```

## Usage

### Running All Tests

```bash
python -m a_bot_tester.runner
```

### Running Specific Test Scenario

```bash
python -m a_bot_tester.runner --scenario basic_commands
```

### Interactive Mode

```bash
python -m a_bot_tester.interactive
```

## Test Scenarios

Test scenarios are defined in `scenarios/` directory in YAML format:

```yaml
name: Basic Commands Test
description: Test basic bot commands

tests:
  - name: Start Command
    command: /start
    expected:
      - contains: "Welcome"
      - type: message
    timeout: 10

  - name: Help Command
    command: /help
    expected:
      - contains: "Available commands"
    timeout: 10
```

## Project Structure

```
a_bot_tester/
├── src/
│   └── a_bot_tester/
│       ├── __init__.py
│       ├── client.py          # Telethon client wrapper
│       ├── runner.py          # Test runner
│       ├── interactive.py     # Interactive mode
│       ├── validator.py       # Response validators
│       └── reporter.py        # Test report generator
├── scenarios/                 # Test scenario YAML files
├── tests/                     # Unit tests
├── .env.example
├── pyproject.toml
└── README.md
```

## Security Notes

- **Never commit your `.env` file** - it contains sensitive credentials
- **Session files** (`*.session`) are created by Telethon and should not be shared
- Use a separate Telegram account for testing purposes
- The first run will require phone verification via SMS code

## License

MIT License
