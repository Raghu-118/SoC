# SoC
Voice assistant project for SoC Challange
Project Setup

📦 Installation
1. System dependencies
sudo apt update
sudo apt install wget unzip pulseaudio alsa-utils python3-pip

2. Python dependencies
Activate your virtual environment (venv) and install:
pip install vosk sounddevice piper-tts

3. Download Hindi Vosk model
wget https://github.com/alphacep/vosk-api/releases/download/v0.22/vosk-model-small-hi-0.22.zip
unzip vosk-model-small-hi-0.22.zip
mv vosk-model-small-hi-0.22 ~/Local-Voice/

4. Download Piper Hindi voices
Example: Pratham medium voice
mkdir -p ~/Local-Voice/voices
wget https://github.com/rhasspy/piper/releases/download/v0.0.2/hi_IN-pratham-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v0.0.2/hi_IN-pratham-medium.onnx.json
mv hi_IN-pratham-medium.onnx hi_IN-pratham-medium.onnx.json ~/Local-Voice/voices/

▶️ Usage
Run the assistant:
python assistant.py


You’ll see:
== Offline Hindi Voice Assistant ==
🎤 बोलिए... (Ctrl+C to exit)

Speak Hindi commands like:
- “समय क्या है”
- “आज की तारीख क्या है”
- “मज़ाक सुनाओ”
- “गणना करो 12*3”
- “प्रेरणा दो”

📂 Project Structure
Local-Voice/
├── assistant.py
├── voices/
│   ├── hi_IN-pratham-medium.onnx
│   └── hi_IN-pratham-medium.onnx.json
└── vosk-model-small-hi-0.22/
    ├── am/
    ├── conf/
    ├── graph/
    └── README

✅ Notes
- Works fully offline — no cloud calls.
- Designed for Raspberry Pi (Arm SBC) but also runs on Ubuntu/WSL.
- You can add more commands by editing the COMMANDS dictionary in assistant.py.
