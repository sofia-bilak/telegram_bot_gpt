# MultiMode AI Bot

A multi-purpose Telegram bot powered by OpenAI's GPT models. The bot combines several interaction modes — free-form chat, character roleplay, a quiz game, personalized recommendations, and voice conversations — in a single, menu-driven interface.

**Telegram:** [@multimode_ai_bot](https://t.me/multimode_ai_bot)

> ⚠️ This bot is currently for local/development use only and is not deployed to a public server.

---

## Features

| Command | Description |
|---|---|
| `/start` | Shows the welcome message and the main menu |
| `/random` | Sends a random interesting fact, with the option to request more |
| `/gpt` | Free-form chat with ChatGPT |
| `/talk` | Roleplay conversation with a chosen historical/public figure (Kurt Cobain, Queen Elizabeth II, J.R.R. Tolkien, Friedrich Nietzsche, Stephen Hawking) |
| `/quiz` | An interactive quiz on Programming, Math, or Biology, with score tracking and topic switching |
| `/recommend` | Personalized movie, book, or music recommendations based on genre, with the ability to dislike a suggestion and get a new one |
| `/voice` | Voice-based conversation — send a voice message and receive a spoken reply from ChatGPT |

All modes are accessible from the `/start` menu via inline buttons, and most conversations end with a "Finish" button that returns to the main menu.

---

## Project Structure

```
telegram_bot_gpt/
├── main.py           # Entry point — builds the bot and registers all handlers
├── util.py           # Telegram-specific helpers 
├── credentials.py    # Bot token and OpenAI API key (not committed)
├── state.py          # Stores the application's runtime state
├── handlers/
│   ├── start.py             # /start command and main menu
│   ├── random.py            # /random command
│   ├── gpt.py               # /gpt command
│   ├── talk.py              # /talk command and personality selection
│   ├── quiz.py              # /quiz command, topic/question flow, scoring
│   ├── recommend.py         # /recommend command, category/genre flow
│   ├── voice.py             # /voice command and voice message handling
│   └── messages.py          # Central plain-text message router
├── services/
│   ├── chatgpt_service.py    # Wrapper around the OpenAI Chat Completions API
│   ├── voice_service.py      # Wrapper around Whisper transcription + GPT audio responses
│   └── instance.py           # Shared service instances
└── resources/
    ├── images/                # Images sent with each command
    ├── messages/              # Static UI text per command
    └── prompts/               # System prompts sent to ChatGPT per mode
```

---

## How It Works

The bot is built on [python-telegram-bot](https://docs.python-telegram-bot.org/) and uses a simple **mode-based state machine** to decide how to interpret a user's next message:

1. A dictionary `chat_modes` keeps track of each user's current mode (e.g. `GPT_MODE`, `QUIZ_WAITING_FOR_ANSWER_MODE`, `RECOMMEND_WAITING_FOR_GENRE`).
2. `handlers/messages.py` checks this mode whenever plain text arrives and routes it to the right logic.
3. Inline keyboard buttons (`CallbackQueryHandler`) drive category/topic selection and "Finish" actions, and reset the mode back to `None` when a conversation ends.
4. All OpenAI requests go through a single shared client (`services/instance.py`), configured once with the API key (and proxy, if required) and reused by every mode — including voice.

---

## Getting Started

### Prerequisites

- Python 3.10+
- A Telegram bot token
- An OpenAI API key with access to `gpt-4o` / `gpt-4o-mini`, `whisper-1`, and an audio-capable chat model

### Installation

```bash
git clone <repository-url>
cd telegram_bot_gpt

python -m venv venv
source venv/bin/activate 
# on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `credentials.py` file in the project root (this file is gitignored and must never be committed):

```python
BOT_TOKEN = "your-telegram-bot-token"
ChatGPT_TOKEN = "your-openai-api-key"
```

### Running the bot

```bash
python main.py
```

The bot will start polling for updates. Open a chat with it on Telegram and send `/start`.

---

## Resources

Each command relies on three resource files sharing the same base name:

- `resources/images/<name>.jpg` — image shown with the command
- `resources/messages/<name>.txt` — static text shown to the user
- `resources/prompts/<name>.txt` — system prompt sent to ChatGPT for that mode

When adding a new mode, all three files should be created to keep the bot's behavior consistent.

---

## Tech Stack

- [python-telegram-bot](https://docs.python-telegram-bot.org/) — Telegram Bot API wrapper
- [OpenAI Python SDK](https://github.com/openai/openai-python) — Chat Completions, Whisper transcription, audio responses
- Python 3.12 (async/await throughout)

---

## Status & Roadmap

This is an actively developed learning project. Implemented so far:

- [x] Free-form GPT chat
- [x] Random facts
- [x] Character roleplay
- [x] Quiz with scoring and topic switching
- [x] Movie/book/music recommendations with "dislike" feedback
- [x] Voice conversations (speech-to-text + audio reply)

Planned / possible next steps:

- [ ] Per-topic quiz scoring
- [ ] Deployment to a persistent server
- [ ] Global error handler for network/API failures
- [ ] Per-user isolated conversation history (currently a single shared OpenAI client conversation state)
