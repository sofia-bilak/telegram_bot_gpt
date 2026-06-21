from telegram import Update
from telegram.ext import ContextTypes

from util import load_message, send_text, send_image, load_prompt, send_text_buttons
from handlers import start
from services.instance import chat_gpt
from state import chat_modes, quiz_scores


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await send_image(update, context, 'quiz')
    await quiz_show_topics(update, context, user_id)
    chat_gpt.set_prompt(load_prompt('quiz'))
    quiz_scores[user_id] = 0


async def quiz_show_topics(update, context, user_id):
    chat_modes[user_id] = 'QUIZ_MODE'
    await send_text_buttons(
        update, context,
        load_message('quiz'),
        buttons={
            'quiz_prog': 'Програмування',
            'quiz_math': 'Математика',
            'quiz_biology': 'Біологія'
        }
    )


async def quiz_show_question(update, context, user_id, query_for_gpt):
    response = await chat_gpt.add_message(query_for_gpt)
    await send_text(update, context, response)
    chat_modes[user_id] = 'QUIZ_WAITING_FOR_ANSWER_MODE'


async def quiz_end(update, context, user_id):
    final_score = quiz_scores.get(user_id, 0)
    await send_text(update, context, f'Вікторину завершено! Кількість правильних відповідей: {final_score}')
    chat_modes[user_id] = None
    await start(update, context)


async def quiz_buttons_handler(update: Update, context):
    query = update.callback_query.data
    user_id = update.callback_query.from_user.id

    topics = ['quiz_prog', 'quiz_math', 'quiz_biology']

    if query in topics:
        await quiz_show_question(update, context, user_id, query)
    elif query == 'quiz_more':
        await quiz_show_question(update, context, user_id, query)
    elif query == 'quiz_change':
        await quiz_show_topics(update, context, user_id)
    elif query == 'quiz_finish':
        await quiz_end(update, context, user_id)

    await update.callback_query.answer()