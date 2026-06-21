from telegram.ext import (
    filters,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler
)
from handlers.start import start
from handlers.random_fact import random, random_buttons_handler
from handlers.gpt import gpt, gpt_buttons_handler
from handlers.talk import talk, talk_buttons_handler
from handlers.quiz import quiz, quiz_buttons_handler
from handlers.recommend import recommend, recommend_buttons_handler
from handlers.messages import plain_text_handler
from handlers.voice import voice, voice_buttons_handler, voice_message_handler

import credentials


app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(CommandHandler("recommend", recommend))
app.add_handler(CommandHandler('voice', voice))

app.add_handler(CallbackQueryHandler(random_buttons_handler, pattern="^random_.*"))
app.add_handler(CallbackQueryHandler(gpt_buttons_handler, pattern="^gpt_.*"))
app.add_handler(CallbackQueryHandler(talk_buttons_handler, pattern="^talk_.*"))
app.add_handler(CallbackQueryHandler(quiz_buttons_handler, pattern="^quiz_.*"))
app.add_handler(CallbackQueryHandler(recommend_buttons_handler, pattern="^recommend_.*"))
app.add_handler(CallbackQueryHandler(voice_buttons_handler, pattern='^voice_.*'))

app.add_handler(MessageHandler(filters.VOICE, voice_message_handler))
app.add_handler(MessageHandler(None, plain_text_handler))

app.run_polling()