import base64

class VoiceService:
    def __init__(self, client):
        self.client = client

    async def speech_to_text(self, voice_file_path: str, language: str = "uk") -> str:
        try:
            with open(voice_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            return transcript.text
        
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None

    async def generate_audio_response(self, prompt_text: str, message_text: str, output_path: str) -> bool:
        try:
            completion = self.client.chat.completions.create(
                model="gpt-audio-1.5",
                modalities=["text", "audio"],
                audio={"voice": "alloy", "format": "mp3"},
                messages=[
                    {
                        "role": "system",
                        "content": prompt_text
                    },
                    {
                        "role": "user",
                        "content": message_text
                    }
                ]
            )

            message = completion.choices[0].message
            audio_bytes = base64.b64decode(message.audio.data)

            with open(output_path, 'wb') as f:
                f.write(audio_bytes)

            return True

        except Exception as e:
            print(f"Audio response generation error: {e}")
            return False
      

    def cleanup(self, *file_paths):
        import os
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                