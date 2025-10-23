import os
import sys
import cv2
import time
import random
import smtplib
import datetime
import webbrowser
import pyautogui
import requests
import pyttsx3
import wikipedia
import pywhatkit as kit
import speech_recognition as sr
import pyjokes
import PyPDF2
from requests import get
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import Ui_JarvisUi


# ============ TEXT-TO-SPEECH ENGINE ============ #
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 180)


def speak(audio):
    """Convert text to speech."""
    print(f"Jarvis: {audio}")
    engine.say(audio)
    engine.runAndWait()


# ============ GREETING ============ #
def wish():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning Sir!")
    elif 12 <= hour < 18:
        speak("Good Afternoon Sir!")
    else:
        speak("Good Evening Sir!")
    speak("I am Jarvis, please tell me how may I assist you.")


# ============ EMAIL SENDER ============ #
def send_email(to, content):
    try:
        sender_email = os.getenv("JARVIS_EMAIL")
        sender_pass = os.getenv("JARVIS_PASS")

        if not sender_email or not sender_pass:
            speak("Email credentials not configured.")
            return

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, to, content)
        server.quit()
        speak("Email has been sent successfully!")
    except Exception as e:
        print("Email error:", e)
        speak("Sorry sir, I am not able to send this email.")


# ============ PDF READER ============ #
def pdf_reader():
    try:
        file_path = input("Enter full PDF file path: ").strip('"')
        if not os.path.exists(file_path):
            speak("File not found, please check the path.")
            return

        book = open(file_path, 'rb')
        pdfreader = PyPDF2.PdfReader(book)
        pages = len(pdfreader.pages)
        speak(f"This file has {pages} pages. Which page should I read?")
        pg = int(input("Page number: "))
        if 0 <= pg < pages:
            text = pdfreader.pages[pg].extract_text()
            speak(text if text else "No readable text found on that page.")
        else:
            speak("Page number out of range.")
    except Exception as e:
        speak("Error reading the PDF.")
        print("PDF error:", e)


# ============ SCREENSHOT ============ #
def take_screenshot():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"
    image = pyautogui.screenshot()
    image.save(filename)
    speak(f"Screenshot saved as {filename} in the current folder.")


# ============ LISTEN FOR COMMAND ============ #
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
            return query.lower()
        except:
            return "none"


# ============ MAIN THREAD ============ #
class JarvisThread(QThread):
    def run(self):
        wish()
        while True:
            query = take_command()
            if query == "none":
                continue

            if "open notepad" in query:
                os.startfile("C:\\Windows\\system32\\notepad.exe")

            elif "close notepad" in query:
                os.system("taskkill /f /im notepad.exe")
                speak("Closed Notepad.")

            elif "open camera" in query:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    speak("Unable to access camera.")
                else:
                    speak("Press ESC to close the camera.")
                    while True:
                        ret, frame = cap.read()
                        cv2.imshow('Camera', frame)
                        if cv2.waitKey(1) == 27:
                            break
                    cap.release()
                    cv2.destroyAllWindows()

            elif "ip address" in query:
                try:
                    ip = get('https://api.ipify.org').text
                    speak(f"Your IP address is {ip}")
                except:
                    speak("Couldn't retrieve IP address.")

            elif "open youtube" in query:
                webbrowser.open("https://youtube.com")

            elif "open google" in query:
                speak("What should I search for?")
                topic = take_command()
                if topic != "none":
                    webbrowser.open(f"https://www.google.com/search?q={topic}")

            elif "play song" in query:
                music_dir = "E:\\music"
                if os.path.isdir(music_dir):
                    songs = os.listdir(music_dir)
                    if songs:
                        os.startfile(os.path.join(music_dir, random.choice(songs)))
                    else:
                        speak("No songs found.")
                else:
                    speak("Music folder not found.")

            elif "switch window" in query or "change window" in query:
                speak("Switching window, sir.")
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(1)
                pyautogui.keyUp("alt")

            elif "wikipedia" in query:
                speak("Searching Wikipedia...")
                topic = query.replace("wikipedia", "").strip()
                try:
                    results = wikipedia.summary(topic, sentences=2)
                    speak("According to Wikipedia")
                    speak(results)
                except:
                    speak("No results found.")

            elif "tell me a joke" in query:
                speak(pyjokes.get_joke())

            elif "exit" in query or "quit" in query:
                speak("Goodbye sir. Have a nice day!")
                sys.exit()

            else:
                speak("I'm not sure how to handle that, sir.")


# ============ SIMPLE GUI ============ #
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_JarvisUi()
        self.ui.setupUi(self)
        self.thread = JarvisThread()
        self.ui.startButton.clicked.connect(self.start_jarvis)

    def start_jarvis(self):
        speak("Starting Jarvis.")
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    jarvis_gui = Main()
    jarvis_gui.show()
    sys.exit(app.exec_())
