# Drops Tracker Bot

A Telegram bot to track airdrop progress and manage airdrop data.

## Features

- Add new airdrop data
- Edit existing airdrop data
- Remove airdrop data
- View airdrop progress with pagination

## Requirements

- Python 3.8+
- Telegram Bot API token
- `python-telegram-bot` library
- `python-dotenv` library

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/rizalrorschach/drops-tracker-bot
   cd drops-tracker-bot
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your Telegram Bot API token:
   ```env
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   ```

## Usage

1. Run the bot:

   ```sh
   python main.py
   ```

2. Interact with the bot on Telegram using the following commands:
   - `/start` - Start the bot and see available commands
   - `/add` - Add new airdrop data
   - `/edit` - Edit existing airdrop data
   - `/remove` - Remove airdrop data
   - `/progress` - View airdrop progress

## License

This project is licensed under the MIT License.
