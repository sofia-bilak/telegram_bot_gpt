from telegram import Update
from telegram.ext import ContextTypes

from state import chat_modes, quiz_scores, recommend_state
from handlers import start, random, gpt, talk, quiz, recommend, recommend_send
from util import send_text, load_prompt, send_text_buttons
from services.instance import chat_gpt


async def plain_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = chat_modes.get(update.message.from_user.id)
    text = update.message.text
    if mode is None:

        if text == '/start':
            await start(update, context)
        elif text == '/random':
            await random(update, context)
        elif text == '/gpt':
            await gpt(update, context)
        elif text == '/talk':
            await talk(update, context)
        elif text == '/quiz':
            await quiz(update, context)
        elif text == '/recommend':
            await recommend(update, context)
        else:
            await send_text(update, context, 'I dont know such command. Use /start command for information!')

    elif mode == 'GPT_MODE':
        pt = load_prompt('gpt')
        response = await chat_gpt.send_question(pt, update.message.text)
        # await send_text(update, context, response)
        # chat_modes[update.message.from_user.id] = None
        await send_text_buttons(
            update, context, response,
            {
                'gpt_finish': 'Закінчити',
            }
        )
    elif mode == 'TALK_MODE':
        response = await chat_gpt.add_message(text)
        await send_text_buttons(
            update, context, response,
            {
                'talk_finish': 'Закінчити',
            }
        )
    elif mode == 'QUIZ_WAITING_FOR_ANSWER_MODE':
        answer = await chat_gpt.add_message(text)
        if answer.strip().lower().startswith('правильно'):
            quiz_scores[update.message.from_user.id] += 1
        await send_text(update, context, answer)
        await send_text(update, context, f'Ваш рахунок: {quiz_scores[update.message.from_user.id]}')
        await send_text_buttons(
            update, context, 
            'Що робимо далі?',
            {
                'quiz_more': 'Ще питання на ту ж тему',
                'quiz_change': 'Змінити тему вікторини',
                'quiz_finish': 'Закінчити вікторину'
            }
        )
        chat_modes[update.message.from_user.id] = 'QUIZ_MODE'
    elif mode == 'RECOMMEND_WAITING_FOR_GENRE':
        user_id = update.message.from_user.id
        recommend_state[user_id]['genre'] = text
        await recommend_send(update, context, user_id)