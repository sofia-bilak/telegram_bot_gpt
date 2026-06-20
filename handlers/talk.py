from telegram import Update
from telegram.ext import ContextTypes

from util import load_message, send_text, send_image, load_prompt, send_text_buttons
from handlers.start import start
from services.instance import chat_gpt
from state import chat_modes


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'TALK_MODE'
    await send_image(update, context, 'talk')
    await send_text_buttons(
        update, context,
        load_message('talk'),
        buttons={
            'talk_cobain': 'Курт Кобейн',
            'talk_queen': 'Єлизавета II',
            'talk_tolkien': 'Джон Толкін',
            'talk_nietzsche': 'Фрідріх Ніцше',
            'talk_hawking': 'Стівен Гокінг'
        }
    )


async def talk_buttons_handler(update: Update, context):
    query = update.callback_query.data

    personalities = {
        'talk_cobain': ('talk_cobain', 'Курт Кобейн'),
        'talk_queen': ('talk_queen', 'Єлизавета II'),
        'talk_tolkien': ('talk_tolkien', 'Джон Толкін'),
        'talk_nietzsche': ('talk_nietzsche', 'Фрідріх Ніцше'),
        'talk_hawking': ('talk_hawking', 'Стівен Гокінг'),
    }
    
    if query == 'talk_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update, context)
    elif query in personalities:
        prompt_name, personality = personalities[query]
        chat_gpt.set_prompt(load_prompt(prompt_name))
        await send_image(update, context, prompt_name)
        await send_text(update, context, f"Тепер ви спілкуєтеся з {personality}")

    await update.callback_query.answer()