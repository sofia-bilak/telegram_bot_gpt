from http.client import responses

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler

from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons)

import credentials

chat_modes = {}
quiz_scores = {}

### 4. *"Квіз"*
# Телеграм-бот повинен обробляти команду /quiz.
# При обробці команди бот надсилає заздалегідь підготовлене зображення
# та пропонує вибір з декількох тем, використовуючи кнопки.
# Після вибору теми, передати запит ChatGPT і, отримавши питання квізу, передати його
# користувачеві. Наступне текстове повідомлення користувача вважається відповіддю.
# Його потрібно передати ChatGPT та отримати результат. Результат передати користувачеві
# з можливістю задати ще питання на ту ж тему, змінити тему або закінчити квіз, за допомогою кнопок.
# Бот також повинен вести рахунок правильних відповідей та
# відображати разом з черговим результатом


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
        # Додати команду в меню можна так:
        # 'command': 'button text'

    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('random')
    response = await chat_gpt.send_question(prompt, 'Давай рандомний факт')
    await send_image(update, context, 'random')
    await send_text_buttons(
        update, context,
        response,
        {
            'random_finish' : 'Закінчити',
            'random_one_more' :'Хочу ще факт',
        }
    )


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'GPT_MODE'
    await send_image(update, context, 'gpt')
    await send_text(update, context, load_message('gpt'))


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
            'talk_nietzsсhe': 'Фрідріх Ніцше',
            'talk_hawking': 'Стівен Гокінг'
        }
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_modes[update.message.from_user.id] = 'QUIZ_MODE'
    await send_image(update, context, 'quiz')
    await send_text_buttons(
        update, context,
        load_message('quiz'),
        buttons={
            'quiz_prog': 'Програмування',
            'quiz_math': 'Математика',
            'quiz_biology': 'Біологія',
            'quiz_more': 'Ще питання на ту ж саму тему'
        }
    )
    chat_gpt.set_prompt(load_prompt('quiz'))
    quiz_scores[update.message.from_user.id] = 0




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
        if answer == 'Правильно!':
            quiz_scores[update.message.from_user.id] += 1
        await send_text(update, context, answer)
        await send_text(update, context, f'Your score -> {quiz_scores[update.message.from_user.id]}')
        chat_modes[update.message.from_user.id] = 'QUIZ_MODE'


async def random_buttons_handler(update: Update, context):
    query = update.callback_query.data
    if query == 'random_finish':
        await start(update, context)
    elif query == 'random_one_more':
        await random(update, context)
    await update.callback_query.answer()

async def gpt_buttons_handler(update: Update, context):
    query = update.callback_query.data
    if query == 'gpt_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update, context)

    await update.callback_query.answer()


async def talk_buttons_handler(update: Update, context):
    query = update.callback_query.data

    if query == 'talk_finish':
        chat_modes[update.callback_query.from_user.id] = None
        await start(update, context)
        await update.callback_query.answer()
        return

    if query == 'talk_cobain':
        chat_gpt.set_prompt(load_prompt('talk_cobain'))
        await send_image(update, context, 'talk_cobain')
        personality = "Курт Кобейн"
    elif query == 'talk_queen':
        chat_gpt.set_prompt(load_prompt('talk_queen'))
        await send_image(update, context, 'talk_queen')
        personality = "Єлизавета II"
    elif query == 'talk_tolkien':
        chat_gpt.set_prompt(load_prompt('talk_tolkien'))
        await send_image(update, context, 'talk_tolkien')
        personality = "Джон Толкін"
    elif query == 'talk_nietzsche':
        chat_gpt.set_prompt(load_prompt('talk_nietzsche'))
        await send_image(update, context, 'talk_nietzsche')
        personality = "Фрідріх Ніцше"
    elif query == 'talk_hawking':
        chat_gpt.set_prompt(load_prompt('talk_hawking'))
        await send_image(update, context, 'talk_hawking')
        personality = "Стівен Гокінг"

    await send_text(update, context, f"Тепер ви спілкуєтеся з {personality}")
    await update.callback_query.answer()


async def quiz_buttons_handler(update: Update, context):
    query = update.callback_query.data
    response = await chat_gpt.add_message(query)
    await send_text(update, context, response)
    chat_modes[update.callback_query.from_user.id] = 'QUIZ_WAITING_FOR_ANSWER_MODE'
    await update.callback_query.answer()


chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

# Зареєструвати обробник команди можна так:
app.add_handler(MessageHandler(None, plain_text_handler))

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))


# Зареєструвати обробник колбеку можна так:
app.add_handler(CallbackQueryHandler(random_buttons_handler, pattern='^random_.*'))
app.add_handler(CallbackQueryHandler(gpt_buttons_handler, pattern='^gpt_.*'))
app.add_handler(CallbackQueryHandler(talk_buttons_handler, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(quiz_buttons_handler, pattern='^quiz_.*'))
# app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
