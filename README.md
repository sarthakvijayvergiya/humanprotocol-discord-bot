# Human Protocol Discord Bot

A Discord bot for launching jobs, setting API keys, and configuring result channels for the Human Protocol.

## Project Structure

- `bot.py`: The main entry point for the Discord bot.
- `cogs/`: Contains Discord bot commands organized into cog modules.
- `database/`: Includes database-related code for storing user settings.
- `services/`: Contains external service handlers, including the ExternalAPIHandler.
- `.env`: Configuration file for storing sensitive information like the bot's token.
- `config.json`: Configuration file for storing bot-related settings.

## Inspiration

Repo Structure Inspired by [kkrypt0nn's GitHub](https://github.com/kkrypt0nn).

## Usage

1. Obtain your bot token and add it to the `.env` file or as an environment variable named `TOKEN`.
2. Customize the `config.json` file with your desired bot settings.
3. Install the required Python packages with `python -m pip install -r requirements.txt`.
4. Start the bot with `python bot.py`.

## Issues or Questions

If you encounter any issues or have questions about the bot's functionality, feel free to:
- Post your inquiries on the [GitHub Issues](https://github.com/sarthakvijayvergiya/humanprotocol-discord-bot/issues) page.

We're here to help and provide assistance!

## License

This project is open-source and available under the [MIT License].
