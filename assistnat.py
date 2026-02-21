#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline Hindi Voice Assistant (Raspberry Pi / Ubuntu / WSL)
- Listens to Hindi voice commands via microphone (ASR: Vosk)
- Handles 10+ predefined queries (time, date, greetings, weather, jokes, etc.)
- Speaks responses using Piper TTS
- Runs fully offline
"""

import datetime
import random
import subprocess
import tempfile
import os
import wave
import re
import sys
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ------------------- CONFIG -------------------

BASE_DIR = os.path.dirname(__file__)
VOICE_MODEL = os.path.join(BASE_DIR, "voices", "hi_IN-pratham-medium.onnx")
VOICE_CONFIG = VOICE_MODEL + ".json"
PIPER_PATH = "piper"
RATE = 16000
CHANNELS = 1

# Path to Vosk Hindi model (must match folder name exactly)
VOSK_MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-hi-0.22")

# ------------------- PREDEFINED RESPONSES -------------------

def get_time():
    ist_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    return f"अभी का समय है {ist_now.hour} बजकर {ist_now.minute} मिनट।"

def get_date():
    today = datetime.date.today()
    return f"आज की तारीख है {today.day}/{today.month}/{today.year}।"

def get_greeting():
    greetings = ["नमस्ते!", "सुप्रभात!", "हैलो!", "राम राम!"]
    return random.choice(greetings)

def get_weather():
    return "अभी मौसम साफ़ है और तापमान लगभग 30 डिग्री सेल्सियस है।"

def get_joke():
    jokes = [
        "एक लड़का किताब पढ़ रहा था, किताब बोली: 'थक गए?' लड़का बोला: 'नहीं, मैं तुम्हारे मज़े ले रहा हूँ!'",
        "टीचर: 'इतिहास क्यों पढ़ते हो?' छात्र: 'पता चल सके कि आपके जैसे लोग पहले क्या कर चुके हैं!'"
    ]
    return random.choice(jokes)

def get_name():
    return "मेरा नाम हिंदी सहायक है।"

def get_capabilities():
    return "मैं समय बता सकता हूँ, तारीख बता सकता हूँ, मज़ाक सुना सकता हूँ, मौसम बता सकता हूँ और गणना कर सकता हूँ।"

def get_day():
    today = datetime.date.today()
    days = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    return f"आज {days[today.weekday()]} है।"

def calculate_expression(user_text):
    try:
        expr = user_text.replace("गणना", "").replace("करो", "").strip()
        result = eval(expr)
        return f"उत्तर है {result}।"
    except Exception:
        return "माफ़ करें, मैं यह गणना नहीं कर सका।"

def get_motivation():
    quotes = [
        "कभी हार मत मानो, कोशिश करने वालों की हार नहीं होती।",
        "सपने वो नहीं जो सोते समय आते हैं, सपने वो हैं जो आपको सोने नहीं देते।",
        "मेहनत का फल मीठा होता है।"
    ]
    return random.choice(quotes)

# ------------------- COMMANDS -------------------

COMMANDS = {
    "समय": get_time,
    "तारीख": get_date,
    "नमस्ते": get_greeting,
    "हैलो": get_greeting,
    "मौसम": get_weather,
    "मज़ाक": get_joke,
    "नाम": get_name,
    "कर सकते": get_capabilities,
    "दिन": get_day,
    "गणना": calculate_expression,
    "प्रेरणा": get_motivation,
}

# ------------------- TTS -------------------

def speak(text):
    """Speak Hindi text using Piper + paplay"""
    clean = re.sub(r"[\*]+", '', text)
    clean = re.sub(r"\(.*?\)", '', clean)
    clean = re.sub(r"<.*?>", '', clean)
    clean = clean.replace('\n', ' ').strip()
    clean = re.sub(r'\s+', ' ', clean)

    try:
        piper_proc = subprocess.Popen(
            [PIPER_PATH, "-m", VOICE_MODEL, "-c", VOICE_CONFIG, "--output_raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        tts_pcm, _ = piper_proc.communicate(input=clean.encode())

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            with wave.open(f, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(RATE)
                wf.writeframes(tts_pcm)
            wav_file = f.name

        subprocess.run(["paplay", wav_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(wav_file)

    except Exception as e:
        print(f"[Error] TTS failed: {e}")

# ------------------- ASR -------------------

def listen_and_recognize():
    """Listen from mic and return recognized Hindi text"""
    if not os.path.exists(VOSK_MODEL_PATH):
        print("[Error] Vosk Hindi model not found. Download and place in project folder.")
        sys.exit(1)

    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, RATE)
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=RATE, blocksize=8000, device=None,
                           dtype='int16', channels=CHANNELS, callback=callback):
        print("🎤 बोलिए... (Ctrl+C to exit)")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get("text"):
                    return result["text"]

# ------------------- MAIN LOOP -------------------

def main():
    print("== Offline Hindi Voice Assistant ==\n")
    while True:
        try:
            user_text = listen_and_recognize()
            print("आप:", user_text)

            if any(exit_word in user_text for exit_word in ["बाहर", "exit", "quit"]):
                response = "अलविदा! फिर मिलेंगे।"
                print("सहायक:", response)
                speak(response)
                break

            response = ""
            for cmd, func in COMMANDS.items():
                if cmd in user_text:
                    response = func(user_text) if func == calculate_expression else func()
                    break

            if not response:
                response = "मुझे माफ़ करें, मैं उसका उत्तर नहीं जानता।"

            print("सहायक:", response)
            speak(response)

        except KeyboardInterrupt:
            print("\n[Stopped]")
            break

if __name__ == "__main__":
    main()
