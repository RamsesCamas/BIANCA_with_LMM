import whisper
import pyaudio
import wave
import os
import ffmpeg
import threading

from PIL import Image, ImageTk
from tkinter import Tk,Button, PhotoImage, Label

import openai
from elevenlabs import set_api_key
from elevenlabs import clone, generate, voices, play

from dotenv import load_dotenv

load_dotenv()
set_api_key(os.environ["ELEVEN_LABS_KEY"])
openai.api_key = os.environ["OPENAI_KEY"]


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 7
WAVE_OUTPUT_FILENAME = "grabacion_temporal.wav"
MP3_OUTPUT_FILENAME = "grabacion_temporal.mp3"

voices = voices()
WAIFU_VOICE = voices[-1]

model = whisper.load_model("small")

def speech_to_text(audio_file:str):
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions(fp16 = False)
    result = whisper.decode(model, mel, options)
    # print the recognized text
    print(result.text)
    return result.text


def record_audio():
    audio = pyaudio.PyAudio()
    # configurar la grabación de audio
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Grabando audio...")
    # grabar audio en un archivo temporal
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    # cerrar el stream de audio
    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("Grabación finalizada.")
    # guardar el archivo de audio temporal como archivo .wav
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    print("Archivo de audio temporal guardado como " + WAVE_OUTPUT_FILENAME)
    import ffmpeg
    (
        ffmpeg
        .input(WAVE_OUTPUT_FILENAME)
        .output(MP3_OUTPUT_FILENAME, format='mp3')
        .run()
    )

    print("Archivo de audio temporal convertido a " + MP3_OUTPUT_FILENAME)
    # eliminar el archivo temporal
    os.remove(WAVE_OUTPUT_FILENAME)
    print("Archivo de audio temporal eliminado")


def send_commands():
    record_audio()
    command = speech_to_text(MP3_OUTPUT_FILENAME)
    command = command.lower()
    os.remove(MP3_OUTPUT_FILENAME)
    if 'hola' in command and 'bianca' in command:
        run_chatgpt('Saluda de manera formal, presentandote como BIANCA, un asistente virtual potenciado por inteligencia artificial.')
    else:
        run_chatgpt(command)

def run_chatgpt(prompt:str):
    completion = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens = 2048
    )
    result = completion.choices[0].text
    audio = generate(text=result, voice=WAIFU_VOICE, model='eleven_multilingual_v1')

    play(audio)

class App(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()
    
    def run(self):
        root = Tk()
        root.geometry('500x600')
        root.title('B.I.A.N.C.A')
        waifu_img = Image.open("imgs/waifu.png")
        test = ImageTk.PhotoImage(waifu_img)

        label1 = Label(image=test)
        label1.image = test
        label1.place(x=60,y=0)
        microphone_img = PhotoImage(file=r'imgs/microphone.png')
        microphone_img = microphone_img.subsample(4,4)
        btn_micro = Button(root,text='Click me',image=microphone_img,command=send_commands)
        btn_micro.place(x=150,y=425)
        root.mainloop()

if __name__ == '__main__':
    app = App()