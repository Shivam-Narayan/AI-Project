from deep_translator import GoogleTranslator
from gtts import gTTS
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment



transcription = "Good Morning Everyone, I'm working on language translation"
language = 'kn'
output_device_index = 7

def play_audio(file_path, device=output_device_index):
    audio = AudioSegment.from_mp3(file_path)
    audio = audio.set_frame_rate(44100)
    samples = np.array(audio.get_array_of_samples())
    sd.play(samples, samplerate=48000, device=device)
    sd.wait()

def play(transcription, language):
    translation = GoogleTranslator(source='auto', target=language).translate(transcription)
    if not translation.strip():
        print(f"Empty translation for language {language}, skipping...")
    
    print(f"Translation in {language}: {translation}")
    tts = gTTS(text=translation, lang=language, slow=False)
    filename = f"translation_audio_{language}.mp3"
    tts.save(filename)
    play_audio(filename)


play(transcription, language)