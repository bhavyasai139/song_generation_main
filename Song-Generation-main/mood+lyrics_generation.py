import pyaudio
import wave
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np
import re
import pretty_midi
import random
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your valid API key

# Audio recording settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 7
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"


# 🎤 Record audio
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("🎤 Recording... Speak now!")
    frames = [stream.read(CHUNK) for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS))]

    print("✅ Recording complete.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))


# 🎚️ Classify mood from voice (volume + duration)
def classify_voice_mood():
    audio = AudioSegment.from_wav(WAVE_OUTPUT_FILENAME)
    rms = np.mean(np.array(audio.get_array_of_samples()) ** 2) ** 0.5
    nonsilent_parts = detect_nonsilent(audio, min_silence_len=200, silence_thresh=-40)
    speech_duration = sum([end - start for start, end in nonsilent_parts])

    if rms < 1200 and speech_duration < 1500:
        return "Sad"
    elif rms > 4000 and speech_duration > 3500:
        return "Angry"
    else:
        return "Happy"


# 📜 Transcribe audio
def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except (sr.UnknownValueError, sr.RequestError):
            return ""


# 🧠 Analyze emotional tone from text
def analyze_emotion(text):
    if not text.strip():
        return "Neutral"

    prompt = f"""
    Analyze the transcribed speech and identify the mood.
    Return only one mood from: Happy, Excited, Romantic, Sad, Angry, Haunting.
    Transcription: {text}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, "text") else "Neutral"


# 🎭 Compare voice mood vs text mood
def compare_moods(voice_mood, text_mood):
    happy = ["Happy", "Excited", "Romantic"]
    sad = ["Sad"]
    other = ["Angry", "haunting"]

    if text_mood in happy and voice_mood == "Happy":
        return text_mood
    elif text_mood in sad and voice_mood == "Sad":
        return text_mood
    elif text_mood in other and voice_mood == text_mood:
        return text_mood
    else:
        print(f"🎭 Voice suggests {voice_mood}, but text suggests {text_mood}")
        return text_mood  # fallback to text-based mood


# 📝 Generate lyrics using Gemini
def generate_lyrics(prompt_mood, text):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(
        f"Generate song lyrics in English with rhyme and rhythm, in a {prompt_mood} mood using the text: {text} Limit to 2 lines."
    )
    return response.text.strip()


# 🔡 Syllable estimation
def extract_syllables(lyrics):
    words = lyrics.split()
    syllables = [max(1, len(re.findall(r"[aeiouAEIOU]+", word))) for word in words]
    return words, syllables


# 🎼 Generate melody from syllables
def generate_melody(words, syllables, scale_type="major"):
    scales = {
        "major": [60, 62, 64, 65, 67, 69, 71, 72],
        "minor": [60, 62, 63, 65, 67, 68, 70, 72],
    }
    scale = scales[scale_type]
    melody, durations = [], []
    for word, count in zip(words, syllables):
        note = random.choice(scale)
        melody.extend([note] * count)
        durations.extend([0.5] * count)
    return melody, durations


# 💾 Save MIDI
def save_midi(melody, durations, filename="generated_melody.mid"):
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)
    start = 0
    for note, dur in zip(melody, durations):
        midi_note = pretty_midi.Note(
            velocity=100, pitch=note, start=start, end=start + dur
        )
        instrument.notes.append(midi_note)
        start += dur
    pm.instruments.append(instrument)
    pm.write(filename)
    print(f"🎶 MIDI file saved as {filename}")


# 🚀 Full pipeline
def main():
    record_audio()
    voice_mood = classify_voice_mood()
    print(f"🧠 Voice Mood: {voice_mood}")

    text = transcribe_audio()
    print(f"📝 Transcription: {text}")

    text_mood = analyze_emotion(text)
    print(f"🧠 Text Mood: {text_mood}")

    # Ask user if moods conflict
    if voice_mood != text_mood:
        print(
            f"⚠️ Conflict detected between voice mood ('{voice_mood}') and text mood ('{text_mood}')."
        )
        print("❓ Which mood would you like to use?")
        print("1. Voice mood:", voice_mood)
        print("2. Text mood:", text_mood)

        while True:
            choice = input("Enter 1 or 2: ").strip()
            if choice == "1":
                final_mood = voice_mood
                break
            elif choice == "2":
                final_mood = text_mood
                break
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
    else:
        final_mood = text_mood  # or voice_mood, since they match

    print(f"🎼 Generating music for mood: {final_mood}")

    lyrics = generate_lyrics(final_mood, text)
    print(f"\n🎤 Generated Lyrics:\n{lyrics}")

    # words, syllables = extract_syllables(lyrics)
    # scale_type = "major" if final_mood in ["Happy", "Excited", "Romantic", "Joyful", "Energetic"] else "minor"

    # melody, durations = generate_melody(words, syllables, scale_type)
    # if melody:
    #     save_midi(melody, durations)
    # else:
    #     print("⚠️ No melody generated. Try again.")


if __name__ == "__main__":
    main()
