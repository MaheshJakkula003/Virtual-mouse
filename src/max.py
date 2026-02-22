import pyttsx3
import speech_recognition as sr
import cv2
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import wikipedia
import app
from threading import Thread

# Gesture controller with virtual mouse
import Gesture_Controller

# -------- Initialization --------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

file_exp_status = False
files = []
path = ''
is_awake = True
gesture_active = False
gesture_thread = None
gesture_should_stop = False

# -------- Response Functions --------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()

def wish():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        reply("Good Morning!")
    elif hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")
    reply("I am Max, how may I help you?")

# -------- Voice Input --------
def record_audio():
    with sr.Microphone() as source:
        r.energy_threshold = 500
        r.pause_threshold = 0.8
        try:
            audio = r.listen(source, phrase_time_limit=5)
            return r.recognize_google(audio).lower()
        except:
            return ""

# -------- Gesture Stop Checker --------
def should_stop_gesture():
    return gesture_should_stop

# -------- Respond Function --------
def respond(voice_data):
    global file_exp_status, files, path, is_awake, gesture_active
    global gesture_should_stop, gesture_thread

    voice_data = voice_data.lower().replace("max", "").strip()
    print("Command:", voice_data)
    app.eel.addUserMsg(voice_data)

    if not is_awake and "wake up" in voice_data:
        is_awake = True
        wish()
        return

    if "hello" in voice_data:
        wish()

    elif "name" in voice_data:
        reply("My name is Max!")

    elif "date" in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif "time" in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif "search" in voice_data:
        query = voice_data.split("search")[-1]
        reply(f"Searching for {query}")
        webbrowser.open(f"https://google.com/search?q={query}")

    elif "location" in voice_data:
        reply("Which location?")
        location = record_audio()
        reply("Locating...")
        webbrowser.open(f"https://google.com/maps/place/{location}")

    elif "wikipedia" in voice_data:
        query = voice_data.replace("wikipedia", "")
        try:
            results = wikipedia.summary(query, sentences=2)
            reply(results)
        except Exception:
            reply("Sorry, I couldn't find that on Wikipedia.")

    elif "open" in voice_data:
        app_name = voice_data.replace("open", "").strip()
        try:
            os.system(f"start {app_name}")
            reply(f"Opening {app_name}")
        except:
            try:
                os.startfile(app_name)
                reply(f"Launching {app_name}")
            except:
                reply(f"Sorry, I couldn't find {app_name} on your system.")

    elif "launch gesture" in voice_data:
        if gesture_active:
            reply("Gesture recognition is already active")
        else:
            gesture_should_stop = False
            Gesture_Controller.set_should_stop_callback(should_stop_gesture)
            gesture_thread = Thread(target=Gesture_Controller.start_gesture_control)
            gesture_thread.start()
            gesture_active = True
            reply("Gesture recognition started")

    elif "stop gesture" in voice_data:
        if gesture_active:
            gesture_should_stop = True
            if gesture_thread:
                gesture_thread.join()
            gesture_active = False
            reply("Gesture recognition stopped")
        else:
            reply("Gesture recognition is not active")

    elif "copy" in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press("c")
            keyboard.release("c")
        reply("Copied")

    elif "paste" in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press("v")
            keyboard.release("v")
        reply("Pasted")

    elif "list files" in voice_data:
        path = "C://"
        files = listdir(path)
        filestr = "<br>".join([f"{i+1}: {f}" for i, f in enumerate(files)])
        file_exp_status = True
        reply("Here are your files:")
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status:
        try:
            index = int(voice_data.split()[-1]) - 1
            selected_file = files[index]
            full_path = join(path, selected_file)
            if isfile(full_path):
                os.startfile(full_path)
                file_exp_status = False
                reply("File opened")
            else:
                path = join(path, selected_file)
                files = listdir(path)
                filestr = "<br>".join([f"{i+1}: {f}" for i, f in enumerate(files)])
                reply("Folder opened")
                app.ChatBot.addAppMsg(filestr)
        except:
            reply("Could not open the file or folder")

    elif "back" in voice_data and file_exp_status:
        if path == "C://":
            reply("Already at root directory")
        else:
            path = "//".join(path.split("//")[:-2]) + "//"
            files = listdir(path)
            filestr = "<br>".join([f"{i+1}: {f}" for i, f in enumerate(files)])
            reply("Moved back")
            app.ChatBot.addAppMsg(filestr)

    elif "exit" in voice_data or "terminate" in voice_data:
        if gesture_active:
            gesture_should_stop = True
            if gesture_thread:
                gesture_thread.join()
        app.ChatBot.close()
        reply("Exiting...")
        sys.exit()

    elif "bye" in voice_data:
        reply("Goodbye!")
        is_awake = False

    else:
        reply("I'm not yet programmed to handle that request.")

# -------- Main Loop --------
t1 = Thread(target=app.ChatBot.start)
t1.start()

while not app.ChatBot.started:
    time.sleep(0.5)

wish()

while True:
    try:
        voice_data = app.ChatBot.popUserInput() if app.ChatBot.isUserInput() else record_audio()
        if "max" in voice_data:
            respond(voice_data)
    except SystemExit:
        break
    except Exception as e:
        print(f"Error: {e}")
        reply("Something went wrong.")
