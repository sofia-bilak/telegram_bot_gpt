from telegram import Update
from telegram.ext import ContextTypes

from util import load_message, send_text, send_image
from handlers import start
from state import chat_modes


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'GPT_MODE'
    await send_image(update, context, 'gpt')
    await send_text(update, context, load_message('gpt'))


async def gpt_buttons_handler(update: Update, context):
    query = update.callback_query.data
    if query == 'gpt_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update, context)

    await update.callback_query.answer()