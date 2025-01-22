import pyttsx3
import os
import subprocess as sp
import speech_recognition as sr
import threading
from pynput import keyboard
from decouple import config
from datetime import datetime
from random import choice
from conv import randomtext
from online import findIP, search_on_google, search_on_wikipedia, youtube,send_email

# Set environment variable for FLAC_CONVERTER
os.environ["FLAC_CONVERTER"] = "/opt/homebrew/bin/flac"

# Set up speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 175)
voices = engine.getProperty('voices')

USER = config('USER')
HOSTNAME = config('BOT')

# Global variable to manage listening status
listening = False

# Dictionary of application commands and their corresponding paths
applications = {
    "terminal": "/usr/bin/open -a Terminal",
    "camera": "/usr/bin/open -a Photo Booth",
    "whatsapp": "/usr/bin/open -a whatsapp",
    "vs code": "/usr/bin/open -a 'Visual Studio Code'",
    "notes": "/usr/bin/open -a notes",
    "notepad": "/usr/bin/open -a TextEdit",
    "settings": "/usr/bin/open -a settings",
    "app store": "/usr/bin/open -a app store",
    "notion": "/usr/bin/open -a notion",
    "brave": "/usr/bin/open -a brave",  
    "safari": "/usr/bin/open -a safari",
    "reminders": "/usr/bin/open -a reminders",
    "calendar": "/usr/bin/open -a calendar",
    "face time": "/usr/bin/open -a 'FaceTime'",
    "music": "/usr/bin/open -a music",  
    "weather": "/usr/bin/open -a weather",
    "clock": "/usr/bin/open -a clock",
}

# Function to speak text
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
    finally:
        engine.stop()

# Greet the user
def greet():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        speak("Good morning")
    elif 12 <= hour < 17:
        speak("Good afternoon")
    elif 17 <= hour <= 23:
        speak("Good evening")
    else:
        speak("Hello")
    speak(f"I am {HOSTNAME}. How may I assist you?")
    print("Press Ctrl to start listening")
    print("Press Cmd to stop listening")

# Start listening for commands
def start_listening():
    global listening
    if not listening:
        listening = True
        print("Started listening")

# Pause listening for commands
def pause_listening():
    global listening
    if listening:
        listening = False
        print("Stopped listening")

# Define hotkeys using pynput
def on_press(key):
    try:
        if key == keyboard.Key.ctrl_l:
            start_listening()
        elif key == keyboard.Key.cmd_l:
            pause_listening()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("Exiting application...")
        return False

# Listen for hotkeys in a separate thread
def listen_for_hotkeys():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Recognize voice commands
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User: {query}")
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand. Can you please repeat?")
            query = "None"
        except sr.RequestError:
            speak("There seems to be an issue with the recognition service.")
            query = "None"
        return query.lower()

# Open an application
def open_application(application_name):
    application_name = application_name.lower()
    if application_name in applications:
        try:
            speak(f"Opening {application_name.capitalize()}")
            sp.Popen(applications[application_name], shell=True)
        except Exception as e:
            speak(f"Failed to open {application_name}. Error: {str(e)}")
    else:
        speak(f"Sorry, I don't know how to open {application_name}.")

# Main function
def main():
    greet()
    while True:
        if listening:
            query = takecommand()
            if "how are you" in query:
                speak("I am absolutely fine. How about you?")
            elif "thanks" in query:
                speak("You're welcome, I'm glad I could help. If you have more questions, feel free to ask.")
            elif "stop" in query or "exit" in query or "bye" in query:
                hour = datetime.now().hour
                if 21 <= hour or hour < 6:
                    speak("Good night")
                else:
                    speak("Have a good day")
                break
            elif "youtube" in query:
                speak("What do you want to play on YouTube?")
                video = takecommand().lower()
                youtube(video)
            elif "open google" in query:
                speak("What do you want to search on Google?")
                query = takecommand().lower()
                search_on_google(query)
            elif "wikipedia" in query:
                speak("What do you want to search on Wikipedia?")
                search = takecommand().lower()
                results = search_on_wikipedia(search)
                speak(f"According to Wikipedia, {results}")
                print(results)
            elif "ip address" in query:
                ip_address = findIP()
                speak(f"Your IP address is {ip_address}")
                print(f"Your IP address is {ip_address}")
            elif "send an email" in query:
                speak("To which email address should I send? Please enter the email address:")
                receiver_add = input("Email address: ").strip()
                speak("What should be the subject?")
                subject = takecommand().capitalize()
                speak("What is the message?")
                message = takecommand()
                if send_email(receiver_add, subject, message):
                    speak("The email has been sent successfully.")
                else:
                    speak("Sorry, I couldn't send the email. Please check the configuration and try again.")
            elif "open" in query:
                command_parts = query.split("open")
                if len(command_parts) > 1:
                    app_name = command_parts[1].strip()
                    open_application(app_name)
            elif query != "none":
                speak(choice(randomtext))
        else:
            continue

# Entry point
if __name__ == '__main__':
    try:
        # Start the hotkey listener in a separate thread
        listener_thread = threading.Thread(target=listen_for_hotkeys)
        listener_thread.daemon = True
        listener_thread.start()
        print("Welcome to Personal AI Assistant")
        
        # Run the main function
        main()
    except KeyboardInterrupt:
        print("\nExiting application gracefully...")



