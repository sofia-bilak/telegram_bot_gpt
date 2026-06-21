from telegram import Update
from telegram.ext import ContextTypes

from state import chat_modes, quiz_scores, recommend_state
from handlers import start, random, gpt, talk, quiz, recommend, recommend_send, voice
from util import send_text, load_prompt, send_text_buttons
from services.instance import chat_gpt


async def handle_gpt(update, context, text):
    pt = load_prompt('gpt')
    response = await chat_gpt.send_question(pt, text)

    await send_text_buttons(
        update, context, response,
        {'gpt_finish': 'Закінчити'}
    )

async def handle_talk(update, context, text):
    response = await chat_gpt.add_message(text)

    await send_text_buttons(
        update, context, response,
        {'talk_finish': 'Закінчити'}
    )

async def handle_quiz_answer(update, context, text):
    user_id = update.message.from_user.id

    answer = await chat_gpt.add_message(text)

    if answer.strip().lower().startswith('правильно'):
        quiz_scores[user_id] += 1

    await send_text(update, context, answer)
    await send_text(update, context, f'Ваш рахунок: {quiz_scores[user_id]}')

    await send_text_buttons(
        update, context,
        'Що робимо далі?',
        {
            'quiz_more': 'Ще питання на ту ж тему',
            'quiz_change': 'Змінити тему вікторини',
            'quiz_finish': 'Закінчити вікторину'
        }
    )

    chat_modes[user_id] = 'QUIZ_MODE'

async def handle_recommend(update, context, text):
    user_id = update.message.from_user.id
    recommend_state[user_id]['genre'] = text

    await recommend_send(update, context, user_id)


message_handlers = {
    'GPT_MODE': handle_gpt,
    'TALK_MODE': handle_talk,
    'QUIZ_WAITING_FOR_ANSWER_MODE': handle_quiz_answer,
    'RECOMMEND_WAITING_FOR_GENRE': handle_recommend
}


async def plain_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mode = chat_modes.get(user_id)
    text = update.message.text

    if mode is None:
        commands = {
            '/start': start,
            '/random': random,
            '/gpt': gpt,
            '/talk': talk,
            '/quiz': quiz,
            '/recommend': recommend,
            '/voice': voice
        }

        handler = commands.get(text)

        if handler:
            await handler(update, context)
        else:
            await send_text(update, context,
                'Я не знаю такої команди. Використайте команду /start для отримання інформації!'
            )
        return

    handler = message_handlers.get(mode)

    if handler:
        await handler(update, context, text)
