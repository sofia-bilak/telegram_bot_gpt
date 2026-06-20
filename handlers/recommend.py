from telegram import Update
from telegram.ext import ContextTypes

from util import load_message, send_text, send_image, load_prompt, send_text_buttons
from handlers import start
from services.instance import chat_gpt
from state import chat_modes, recommend_state


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'recommend')
    await send_text_buttons(
        update, context,
        load_message('recommend'),
        buttons={
            'recommend_movie': 'Фільми',
            'recommend_book': 'Книги',
            'recommend_music': 'Музика'
        }
    )


async def recommend_send(update, context, user_id):
    state = recommend_state[user_id]
    await send_text(update, context, 'Обробляю ваш запит...')
    prompt_text = load_prompt('recommend').format(
        category=state['category'],
        genre=state['genre'],
        disliked=', '.join(state['disliked']) if state['disliked'] else 'немає'
    )
    response = await chat_gpt.send_question(prompt_text, 'Дай рекомендації')
    state['disliked'].append(response)
    await send_image(update, context, state['image'])
    await send_text_buttons(
        update, context, response,
        {
            'recommend_dislike': 'Не подобається',
            'recommend_finish': 'Закінчити'
        }
    )
    chat_modes[user_id] = 'RECOMMEND_MODE'


async def recommend_buttons_handler(update: Update, context):
    query = update.callback_query.data
    user_id = update.callback_query.from_user.id

    categories = {
        'recommend_movie': ('фільми', 'movies'),
        'recommend_book': ('книги', 'books'),
        'recommend_music': ('музика', 'music'),
    }

    if query in categories:
        category, image_name = categories[query]
        recommend_state[user_id] = {
            'category': category,
            'genre': None,
            'disliked': [],
            'image': image_name
        }
        chat_modes[user_id] = 'RECOMMEND_WAITING_FOR_GENRE'
        await send_text(update, context, 'Який жанр вас цікавить?')
    elif query == 'recommend_dislike':
        await recommend_send(update, context, user_id)
    elif query == 'recommend_finish':
        chat_modes[user_id] = None
        await start(update, context)

    await update.callback_query.answer()