# Nova – Python Voice Assistant (Windows Desktop)

A dark-themed desktop voice assistant built with Python and Tkinter.

## Features

- Dark desktop GUI with conversation history
- Microphone speech input (English - India)
- Text-to-speech responses
- Type commands if you do not want to use the microphone
- Tell current time and date
- Open Google, YouTube, Gmail, GitHub, Wikipedia and Stack Overflow
- Google search
- YouTube playback
- Short Wikipedia answers
- Quick-action buttons and clear-chat control

## Requirements

- Windows 10/11
- Python 3.11 (64-bit recommended)
- Microphone and speakers/headphones
- Internet for speech recognition and online search features

Tkinter is included with standard Windows Python installations.

## Run from VS Code

1. Extract this ZIP file.
2. Open the `Voice_Assistant_Desktop` folder in VS Code.
3. Open **Terminal > New Terminal**.
4. Create the virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

6. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

7. Launch the desktop app:

   ```powershell
   python app.py
   ```

You can also double-click `run_app.bat` after installing the requirements.

## Create a Windows EXE

With the virtual environment activated and dependencies installed, double-click `build_exe.bat`, or run:

```powershell
pyinstaller --noconfirm --clean --windowed --name NovaVoiceAssistant --collect-all pyttsx3 --collect-all wikipedia --collect-all pywhatkit app.py
```

The executable will be created at:

```text
dist\NovaVoiceAssistant\NovaVoiceAssistant.exe
```

This command creates an onedir distribution. Keep the entire `NovaVoiceAssistant` folder together when moving or sharing the app. Test it on the target Windows PC; microphone drivers and Windows permissions still apply.

## Example commands

- "Hello"
- "What time is it?"
- "What's today's date?"
- "Open Google"
- "Open YouTube"
- "Open Gmail"
- "Search Python data engineering"
- "Play relaxing music"
- "Who is Alan Turing?"

You can also type these commands in the message box.

## Notes and troubleshooting

- Speech recognition uses Google's online recognition service through the SpeechRecognition library. An internet connection is required.
- Text-to-speech uses pyttsx3 and normally works offline.
- If PyAudio installation fails, confirm Python 3.11 64-bit is selected and share the complete error. Do not download DLL files from untrusted sites.
- If the microphone is not detected, open Windows Settings > Privacy & security > Microphone and allow desktop apps to access it. Then check Settings > System > Sound > Input.
- The app listens only after you click **Start listening**. It does not continuously record in the background.

## Project structure

```text
Voice_Assistant_Desktop/
├── app.py
├── requirements.txt
├── run_app.bat
├── build_exe.bat
├── README.md
└── .gitignore
```

## Resume description

**Nova – Python Voice Assistant**
- Developed a dark-themed desktop voice assistant with a graphical interface using Python and Tkinter.
- Integrated speech recognition and text-to-speech to accept voice commands and provide spoken responses.
- Added quick actions for date/time, website navigation, Google search, YouTube playback and Wikipedia summaries.

**Tech Stack:** Python, Tkinter, SpeechRecognition, PyAudio, pyttsx3, Wikipedia, PyWhatKit.
