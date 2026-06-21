from telegram import Update
from telegram.ext import ContextTypes

from handlers.start import start
from services.instance import voice_gpt
from util import send_text, load_prompt, load_message, send_image, send_audio, send_text_buttons


async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'voice')
    await send_text(update, context, load_message('voice'))


async def load_voice_file(update, context, user_id):
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    voice_path = f'/tmp/voice_{user_id}.ogg'
    await voice_file.download_to_drive(voice_path)
    return voice_path


async def recognize_speech(update, context, voice_path):
    text_input = await voice_gpt.speech_to_text(voice_path, language="uk")
    if text_input:
        await send_text(update, context, f'Ви сказали: {text_input}')
    return text_input


async def get_response(user_id, text_input):
    prompt = load_prompt("voice")
    audio_path = f"/tmp/response_{user_id}.mp3"

    success = await voice_gpt.generate_audio_response(prompt, text_input, audio_path)

    return success, audio_path


async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    voice_path = None
    audio_path = None

    try:
        await send_text(update, context, "Обробляю голос...")

        voice_path = await load_voice_file(update, context, user_id)

        text_input = await recognize_speech(update, context, voice_path)
        if not text_input:
            await send_text(update, context, "Не вдалося розпізнати мовлення.")
            return

        await send_text(update, context, "Генерую відповідь...")

        success, audio_path = await get_response(user_id, text_input)
        if success:
            await send_audio(update, context, audio_path)
        else:
            await send_text(update, context, "Не вдалося згенерувати аудіо")

    except Exception as e:
        await send_text(update, context, f"Сталася помилка: {e}")

    finally:
        voice_gpt.cleanup(voice_path, audio_path)
        
        await send_text_buttons(
            update, context,
            "Надішліть ще одне голосове повідомлення або завершіть розмову",
            {
                "voice_finish": "Закінчити"
            }
        )


async def voice_buttons_handler(update: Update, context):
    query = update.callback_query.data
    if query == 'voice_finish':
        await start(update, context)

    await update.callback_query.answer()
