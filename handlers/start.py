from telegram import Update
from telegram.ext import ContextTypes
from util import load_message, send_text, send_image, show_main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у вікторині ❓',
        'recommend': 'Обрати фільм, книгу чи музику 🔎',
        'voice': 'Спілкуватись з ChatGPT голосовими повідомленнями 🎤'
    })
