# The Ocean+ bot

This is a utility bot for discord servers.

To run the bot locally, go to the folder of the bot and run:
```
python main.py
```

The bot requires 5 environment variables to run:
- `TOKEN`: The bot token from the Discord developer portal.
- `JEYY_API`: The API for the pat command.
- `MISTRAL_API_KEY`: The API key for the prompt and transcribe commands.
- `TOGETHER-API-KEY`: The API key for the Qwen and DeepSeek in the prompt command.
- `PERPLEXITY_API_KEY`: The API key for Perplexity Sonar in the web_search command.