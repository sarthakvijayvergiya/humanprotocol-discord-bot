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

## How to set up

To set up the bot it was made as simple as possible.

### `config.json` file

There is [`config.json`](config.json) file where you can put the
needed things to edit.

Here is an explanation of what everything is:

| Variable                  | What it is                                     |
| ------------------------- | ---------------------------------------------- |
| YOUR_BOT_PREFIX_HERE      | The prefix you want to use for normal commands |
| YOUR_BOT_INVITE_LINK_HERE | The link to invite the bot                     |
| WELCOME_MESSAGE_CHANNEL_ID | The channel id where bot will send message    |

### `.env` file

To set up the token you will have to either make use of the [`.env.example`](.env.example) file, either copy or rename it to `.env` and replace `YOUR_BOT_TOKEN_HERE`, `API_BASE_URL`, `SUPPORTED_NETWORKS`, `RESULT_CHECK_INTERVAL` with your bot's token, human api server url, support network and result interval in seconds.

## How to start

To start the bot you simply need to launch, either your terminal (Linux, Mac & Windows), or your Command Prompt (
Windows)
.

Before running the bot you will need to install all the requirements with this command:

```
python -m pip install -r requirements.txt
```

After that you can start it with

```
python bot.py
```

## Issues or Questions

If you encounter any issues or have questions about the bot's functionality, feel free to:
- Post your inquiries on the [GitHub Issues](https://github.com/sarthakvijayvergiya/humanprotocol-discord-bot/issues) page.

We're here to help and provide assistance!

## License

This project is open-source and available under the [MIT License].
