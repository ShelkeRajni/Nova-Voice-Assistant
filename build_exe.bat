@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pyinstaller.exe" (
  echo PyInstaller not found. Activate your venv and run:
  echo python -m pip install -r requirements.txt
  pause
  exit /b 1
)
".venv\Scripts\pyinstaller.exe" --noconfirm --clean --windowed --name NovaVoiceAssistant --collect-all pyttsx3 --collect-all wikipedia --collect-all pywhatkit app.py
echo.
echo Build complete. See dist\NovaVoiceAssistant\
pause
