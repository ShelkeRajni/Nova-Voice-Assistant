import datetime
import queue
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import wikipedia
except ImportError:
    wikipedia = None

try:
    import pywhatkit
except ImportError:
    pywhatkit = None


BG = "#10111B"
PANEL = "#191B2A"
PANEL_2 = "#202338"
PURPLE = "#8B5CF6"
BLUE = "#38BDF8"
TEXT = "#F4F3FF"
MUTED = "#A5A7BD"
GREEN = "#34D399"
RED = "#FB7185"


class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova • Voice Assistant")
        self.root.geometry("1060x720")
        self.root.minsize(880, 620)
        self.root.configure(bg=BG)

        self.events = queue.Queue()
        self.listening = False
        self.busy = False
        self.recognizer = sr.Recognizer() if sr else None
        self.speech_queue = queue.Queue()
        self.tts_available = pyttsx3 is not None

        self._build_ui()
        self._start_tts_worker()
        self.root.after(100, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._add_message(
            "assistant",
            "Hi! I'm Nova, your desktop voice assistant. Press the microphone and tell me what you need."
        )
        self._set_status("Ready", GREEN)

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(22, 14))

        logo = tk.Canvas(header, width=48, height=48, bg=BG, highlightthickness=0)
        logo.pack(side="left")
        logo.create_oval(3, 3, 45, 45, fill=PURPLE, outline="")
        logo.create_text(24, 24, text="N", fill="white", font=("Segoe UI", 19, "bold"))

        title_box = tk.Frame(header, bg=BG)
        title_box.pack(side="left", padx=12)
        tk.Label(title_box, text="NOVA", bg=BG, fg=TEXT,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(title_box, text="YOUR PERSONAL VOICE ASSISTANT",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")

        self.status_dot = tk.Label(header, text="●", bg=BG, fg=GREEN,
                                   font=("Segoe UI", 13))
        self.status_dot.pack(side="right", padx=(8, 0))
        self.status_label = tk.Label(header, text="Ready", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 10))
        self.status_label.pack(side="right")

        # Main layout
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=28, pady=(4, 18))
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # Chat panel
        chat_panel = tk.Frame(main, bg=PANEL, highlightthickness=1,
                              highlightbackground="#292C42")
        chat_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        chat_panel.grid_rowconfigure(1, weight=1)
        chat_panel.grid_columnconfigure(0, weight=1)

        chat_header = tk.Frame(chat_panel, bg=PANEL)
        chat_header.grid(row=0, column=0, sticky="ew", padx=22, pady=18)
        tk.Label(chat_header, text="Conversation", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        clear_btn = tk.Button(chat_header, text="Clear chat", command=self.clear_chat,
                              bg=PANEL_2, fg=MUTED, activebackground="#30344D",
                              activeforeground=TEXT, relief="flat", bd=0,
                              padx=12, pady=6, cursor="hand2",
                              font=("Segoe UI", 9))
        clear_btn.pack(side="right")

        self.chat = ScrolledText(
            chat_panel, wrap="word", state="disabled", bg=PANEL, fg=TEXT,
            insertbackground=TEXT, relief="flat", bd=0,
            font=("Segoe UI", 10), padx=20, pady=8,
            selectbackground=PURPLE
        )
        self.chat.grid(row=1, column=0, sticky="nsew")
        self.chat.tag_config("assistant_name", foreground=BLUE, font=("Segoe UI", 9, "bold"))
        self.chat.tag_config("user_name", foreground="#C4B5FD", font=("Segoe UI", 9, "bold"))
        self.chat.tag_config("body", foreground=TEXT, font=("Segoe UI", 10))
        self.chat.tag_config("time", foreground=MUTED, font=("Segoe UI", 8))

        # Composer
        composer = tk.Frame(chat_panel, bg=PANEL)
        composer.grid(row=2, column=0, sticky="ew", padx=18, pady=(10, 18))
        composer.grid_columnconfigure(0, weight=1)
        self.entry = tk.Entry(composer, bg=PANEL_2, fg=TEXT, insertbackground=TEXT,
                              relief="flat", bd=0, font=("Segoe UI", 10))
        self.entry.grid(row=0, column=0, sticky="ew", ipady=13, padx=(0, 9))
        self.entry.insert(0, "Type a command here...")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<Return>", lambda _event: self.send_typed_command())
        send_btn = tk.Button(composer, text="Send", command=self.send_typed_command,
                             bg=PURPLE, fg="white", activebackground="#7445D5",
                             activeforeground="white", relief="flat", bd=0,
                             padx=18, pady=10, cursor="hand2",
                             font=("Segoe UI", 9, "bold"))
        send_btn.grid(row=0, column=1)

        # Right sidebar
        side = tk.Frame(main, bg=BG)
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_columnconfigure(0, weight=1)

        mic_card = tk.Frame(side, bg=PANEL, highlightthickness=1,
                            highlightbackground="#292C42")
        mic_card.grid(row=0, column=0, sticky="ew", pady=(0, 13))
        tk.Label(mic_card, text="VOICE CONTROL", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(pady=(19, 7))
        self.mic_canvas = tk.Canvas(mic_card, width=150, height=150,
                                    bg=PANEL, highlightthickness=0)
        self.mic_canvas.pack()
        self.mic_canvas.create_oval(13, 13, 137, 137, fill="#292044", outline="#44336D", width=2)
        self.mic_canvas.create_oval(26, 26, 124, 124, fill=PURPLE, outline="")
        self.mic_canvas.create_text(75, 75, text="🎙", font=("Segoe UI Emoji", 35), fill="white")
        self.mic_button = tk.Button(
            mic_card, text="Start listening", command=self.start_listening,
            bg=PURPLE, fg="white", activebackground="#7445D5",
            activeforeground="white", relief="flat", bd=0,
            padx=18, pady=11, cursor="hand2",
            font=("Segoe UI", 10, "bold")
        )
        self.mic_button.pack(fill="x", padx=20, pady=(8, 10))
        self.listen_hint = tk.Label(mic_card, text="Click to speak", bg=PANEL, fg=MUTED,
                                    font=("Segoe UI", 8))
        self.listen_hint.pack(pady=(0, 18))

        quick = tk.Frame(side, bg=PANEL, highlightthickness=1,
                         highlightbackground="#292C42")
        quick.grid(row=1, column=0, sticky="ew", pady=(0, 13))
        tk.Label(quick, text="QUICK ACTIONS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(16, 10))
        for label, command in [
            ("◷   Tell me the time", "what time is it"),
            ("▦   Today's date", "what is today's date"),
            ("◎   Open Google", "open google"),
            ("▶   Open YouTube", "open youtube"),
        ]:
            tk.Button(quick, text=label, anchor="w",
                      command=lambda c=command: self.handle_command(c),
                      bg=PANEL_2, fg=TEXT, activebackground="#30344D",
                      activeforeground=TEXT, relief="flat", bd=0,
                      padx=12, pady=10, cursor="hand2",
                      font=("Segoe UI", 9)).pack(fill="x", padx=12, pady=3)
        tk.Frame(quick, bg=PANEL, height=10).pack()

        help_card = tk.Frame(side, bg=PANEL, highlightthickness=1,
                             highlightbackground="#292C42")
        help_card.grid(row=2, column=0, sticky="ew")
        tk.Label(help_card, text="TRY SAYING", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(15, 8))
        examples = [
            "“Search Python tutorials”",
            "“Play relaxing music”",
            "“Who is Alan Turing?”",
            "“Open Gmail”",
            "“Stop assistant”",
        ]
        for example in examples:
            tk.Label(help_card, text=example, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=4)
        tk.Frame(help_card, bg=PANEL, height=12).pack()

        footer = tk.Label(self.root, text="NOVA  •  PYTHON DESKTOP ASSISTANT",
                          bg=BG, fg="#666A83", font=("Segoe UI", 8))
        footer.pack(pady=(0, 10))

    def _clear_placeholder(self, _event):
        if self.entry.get() == "Type a command here...":
            self.entry.delete(0, "end")

    def _set_status(self, text, color=MUTED):
        self.status_label.config(text=text)
        self.status_dot.config(fg=color)

    def _add_message(self, role, message):
        self.chat.configure(state="normal")
        name = "YOU" if role == "user" else "NOVA"
        tag = "user_name" if role == "user" else "assistant_name"
        stamp = datetime.datetime.now().strftime("%I:%M %p")
        self.chat.insert("end", f"{name}  ", tag)
        self.chat.insert("end", f"{stamp}\n", "time")
        self.chat.insert("end", f"{message}\n\n", "body")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def clear_chat(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self._add_message("assistant", "Chat cleared. What can I help you with?")

    def _start_tts_worker(self):
        if not self.tts_available:
            return
        def worker():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 170)
                engine.setProperty("volume", 1.0)
                while True:
                    message = self.speech_queue.get()
                    if message is None:
                        break
                    try:
                        engine.say(message)
                        engine.runAndWait()
                    except Exception:
                        pass
            except Exception:
                self.events.put(("status", ("Speech output unavailable", RED)))
        threading.Thread(target=worker, daemon=True).start()

    def speak(self, message):
        if self.tts_available:
            self.speech_queue.put(message)

    def respond(self, message, speak=True):
        self.events.put(("message", ("assistant", message)))
        if speak:
            self.speak(message)

    def send_typed_command(self):
        command = self.entry.get().strip()
        if not command or command == "Type a command here...":
            return
        self.entry.delete(0, "end")
        self.handle_command(command)

    def handle_command(self, command):
        command = command.lower().strip()
        self._add_message("user", command)
        self._set_status("Working...", BLUE)

        def task():
            try:
                result, should_exit = self._execute_command(command)
                self.events.put(("message", ("assistant", result)))
                if self.tts_available:
                    self.speech_queue.put(result)
                if should_exit:
                    self.events.put(("exit", None))
                else:
                    self.events.put(("status", ("Ready", GREEN)))
            except Exception as exc:
                self.events.put(("message", ("assistant", f"Sorry, something went wrong: {exc}")))
                self.events.put(("status", ("Ready", GREEN)))

        threading.Thread(target=task, daemon=True).start()

    def _execute_command(self, command):
        if any(x in command for x in ["exit", "quit", "stop assistant", "goodbye"]):
            return "Goodbye! You can close the app whenever you're ready.", False

        if any(x in command for x in ["hello", "hi", "hey"]):
            return "Hello! How can I help you?", False

        if "time" in command:
            return "The current time is " + datetime.datetime.now().strftime("%I:%M %p") + ".", False

        if "date" in command or "today" in command:
            return "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y") + ".", False

        sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "wikipedia": "https://www.wikipedia.org",
            "stackoverflow": "https://stackoverflow.com",
        }
        for site, url in sites.items():
            if f"open {site}" in command:
                webbrowser.open(url)
                return f"Opening {site}.", False

        if command.startswith("search for ") or command.startswith("search "):
            query = command.replace("search for ", "", 1) if command.startswith("search for ") else command[7:]
            query = query.strip()
            if query:
                webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
                return f"Here are Google search results for {query}.", False
            return "Please tell me what you want to search for.", False

        if command.startswith("play "):
            query = command[5:].strip()
            if query and pywhatkit:
                pywhatkit.playonyt(query)
                return f"Playing {query} on YouTube.", False
            if not pywhatkit:
                return "YouTube playback needs PyWhatKit. Install the project requirements and restart.", False
            return "Tell me what you want to play.", False

        starters = ("who is ", "what is ", "tell me about ", "where is ")
        if command.startswith(starters):
            topic = command
            for starter in starters:
                if topic.startswith(starter):
                    topic = topic[len(starter):].strip()
                    break
            if not wikipedia:
                return "Wikipedia support is not installed. Install the project requirements and restart.", False
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(topic, sentences=2, auto_suggest=True)
                return summary, False
            except wikipedia.exceptions.DisambiguationError:
                return "That topic has multiple meanings. Please be more specific.", False
            except wikipedia.exceptions.PageError:
                return f"I couldn't find {topic} on Wikipedia.", False
            except Exception:
                return "I couldn't retrieve that information. Please check your internet connection.", False

        return ("I don't know that command yet. Try asking for the time, date, "
                "opening a website, searching Google, or playing a YouTube video."), False

    def start_listening(self):
        if self.busy:
            return
        if not sr:
            messagebox.showerror(
                "Speech recognition not installed",
                "Install the packages from requirements.txt, then restart the app."
            )
            return
        self.busy = True
        self.mic_button.config(text="Listening...", state="disabled", bg="#5B3AA8")
        self.listen_hint.config(text="Speak clearly into your microphone")
        self._set_status("Listening...", PURPLE)
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=8)
            self.events.put(("status", ("Recognizing speech...", BLUE)))
            text = self.recognizer.recognize_google(audio, language="en-IN")
            self.events.put(("recognized", text))
        except sr.WaitTimeoutError:
            self.events.put(("message", ("assistant", "I didn't hear anything. Please try again.")))
        except sr.UnknownValueError:
            self.events.put(("message", ("assistant", "Sorry, I couldn't understand that. Please try again.")))
        except sr.RequestError:
            self.events.put(("message", ("assistant", "Speech recognition needs an internet connection.")))
        except OSError:
            self.events.put(("message", ("assistant", "Microphone not found. Check Windows microphone permissions and input settings.")))
        except Exception as exc:
            self.events.put(("message", ("assistant", f"Microphone error: {exc}")))
        finally:
            self.events.put(("listening_done", None))

    def _process_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "message":
                    self._add_message(*payload)
                elif kind == "status":
                    self._set_status(*payload)
                elif kind == "recognized":
                    self.handle_command(payload)
                elif kind == "listening_done":
                    self.busy = False
                    self.mic_button.config(text="Start listening", state="normal", bg=PURPLE)
                    self.listen_hint.config(text="Click to speak")
                    if self.status_label.cget("text") in ("Listening...", "Recognizing speech..."):
                        self._set_status("Ready", GREEN)
                elif kind == "exit":
                    self.root.after(1200, self.root.destroy)
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._process_events)

    def on_close(self):
        try:
            self.speech_queue.put(None)
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
