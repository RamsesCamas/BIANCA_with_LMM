import os
from elevenlabs import set_api_key
from elevenlabs import clone, generate, voices, play
from dotenv import load_dotenv

load_dotenv()
set_api_key(os.environ["ELEVEN_LABS_KEY"])

voices = voices()
voice = voices[-1]
audio = generate(text="Hola a todos", voice=voice)

play(audio)