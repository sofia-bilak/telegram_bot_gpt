from services import ChatGptService
from services import VoiceService
import credentials

chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
voice_gpt = VoiceService(chat_gpt.client)