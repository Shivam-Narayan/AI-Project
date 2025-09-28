import os
import wave
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment
import asyncio
import nest_asyncio

nest_asyncio.apply()
input_device_index = 0  # Change to the correct input device index
output_device_index = 7  # Change to the correct output device index
languages = ['en', 'hi', 'kn']  # List of languages for translation

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def record_chunk(duration=30, samplerate=44100, channels=1, device=input_device_index):
    print("Recording audio...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16', device=device)
    sd.wait()
    return recording

def save_wav(file_path, recording, samplerate=44100):
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(samplerate)
    wf.writeframes(recording)
    wf.close()

def transcribe_chunk(model, file_path):
    segments, info = model.transcribe(file_path, beam_size=7)
    transcription = ''.join(segment.text for segment in segments)
    return transcription

async def play_audio(file_path, device=output_device_index):
    audio = AudioSegment.from_mp3(file_path)
    audio = audio.set_frame_rate(44100)
    samples = np.array(audio.get_array_of_samples())
    sd.play(samples, samplerate=48000, device=device)
    sd.wait()

async def process_chunk(model, chunk_file):
    try:
        transcription = transcribe_chunk(model, chunk_file)
        if not transcription.strip():
            print("Empty transcription, skipping...")
            return
        print(f"Transcription: {transcription}")
        tts = gTTS(text=transcription, lang='en', slow=False)
        filename = "transcription_audio.mp3"
        tts.save(filename)
        await play_audio(filename)
        os.remove(filename)
        for language in languages:
            translation = GoogleTranslator(source='auto', target=language).translate(transcription)
            if not translation.strip():
                print(f"Empty translation for language {language}, skipping...")
                continue
            print(f"Translation in {language}: {translation}")
            tts = gTTS(text=translation, lang=language, slow=False)
            filename = f"translation_audio_{language}.mp3"
            tts.save(filename)
            await play_audio(filename)
            os.remove(filename)
        os.remove(chunk_file)
    except Exception as e:
        print(f"Error in processing chunk: {e}")

async def record_and_process(model):
    while True:
        chunk_file = "temp_chunk.wav"
        recording = await asyncio.to_thread(record_chunk)
        save_wav(chunk_file, recording)
        await process_chunk(model, chunk_file)

async def main():
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    try:
        await record_and_process(model)
    except KeyboardInterrupt:
        print("Stopping...")
if __name__ == "__main__":
    asyncio.run(main())
