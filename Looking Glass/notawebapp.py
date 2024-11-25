import tkinter as tk
import time
import threading
import requests
import json
import speech_recognition as sr
from PIL import Image, ImageTk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cv2
import math
import numpy as np

frame = ""
res = ""

# Placeholder for your Google Sheets API key, Sheet ID, OpenWeatherMap API key and Spotify key

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

# Load pre-trained models
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
age_net = cv2.dnn.readNetFromCaffe('deploy_age.prototxt', 'age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('deploy_gender.prototxt', 'gender_net.caffemodel')

# Define age and gender labels
age_labels = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
gender_labels = ['Male', 'Female']

# Function to fetch data from Google Sheets
def fetch_sheet_data():
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE}?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("values", [])
            reminders = ""
            todos = ""

            for i in range(1, min(len(data), 6)):
                if data[i][2]:
                    reminders += f"- {data[i][2]} @ {data[i][3]}\n"
                    todos += f"- {data[i][4]}\n"

            reminder_label.config(text=reminders)
            todo_label.config(text=todos)
        else:
            print(f"Error fetching data: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

    root.after(5000, fetch_sheet_data)

# Function to fetch weather data
def fetch_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description'].capitalize()
            icon_code = weather_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_response = requests.get(icon_url, stream=True)
            icon_response.raw.decode_content = True
            icon_image = Image.open(icon_response.raw)
            icon_photo = ImageTk.PhotoImage(icon_image)

            weather_icon_label.config(image=icon_photo)
            weather_icon_label.image = icon_photo

            weather_text = f"{CITY.upper()} WEATHER\n{temperature}°C, {description}"
            weather_label.config(text=weather_text)
        else:
            print(f"Error fetching weather data: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

    root.after(600000, fetch_weather)  # Update weather every 600 seconds

# Function to update time
def update_time():
    current_time = time.strftime("%H : %M : %S")
    time_label.config(text=current_time)
    root.after(1000, update_time)

# Function to listen for a wake word
def listen_for_wake_word():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                print("Listening for wake word...")
                audio = recognizer.listen(source, phrase_time_limit=None)

                # Recognize the audio for the wake word
                wake_word = recognizer.recognize_google(audio).lower()
                if "looking glass" in wake_word:
                    print("Wake word detected. Listening for command...")
                    show_animation("Wake word detected!")
                    listen_for_command_once()
            except sr.UnknownValueError:
                # Could not understand audio
                continue
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

# Function to listen for a single command after wake word
def listen_for_command_once():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening for your command...")
            command_label.config(text="Listening...")
            command_label.place(relx=0.5, rely=0.65, anchor="center")

            # Listen for command
            audio = recognizer.listen(source, phrase_time_limit=5)
            command_text = recognizer.recognize_google(audio)
            print(f"Command recognized: {command_text}")
            show_command_text(command_text)
            execute_command(command_text)
        except sr.UnknownValueError:
            print("Could not understand the command.")
            listen_for_command_once()
        except sr.RequestError as e:
            print(f"Error with the recognition service: {e}")

# Function to execute basic commands
def execute_command(command):
    command = command.lower()
    if "play music" in command:
        play_spotify_music()
    elif "pause music" in command:
        pause_spotify_music()
    elif "next song" in command:
        next_spotify_song()
    elif "hide widgets" in command:
        hide_all()
    elif "show widgets" in command:
        show_all()
    elif "cheese" in command:
        capture()
    elif "thank you" in command:
        show_animation("Have a good day! \n Exiting.")
        listen_for_wake_word()
    else:
        print("Command not recognized.")
        listen_for_command_once()

def capture():
    cv2.imwrite("img.png", frame)
    show_animation("Image sent to your device!")
        

# Spotify control functions
def play_spotify_music():
    try:
        devices = sp.devices()
        if devices['devices']:
            active_device = devices['devices'][0]['id']
            sp.start_playback(device_id=active_device)
            show_command_text("Playing music on Spotify")
        else:
            print("No active device found. Please open Spotify on a device.")
            show_command_text("No active Spotify device found.")
    except Exception as e:
        print(f"Error playing music: {e}")


def pause_spotify_music():
    try:
        sp.pause_playback()
        show_command_text("Music paused on Spotify")
    except Exception as e:
        print(f"Error pausing music: {e}")


def next_spotify_song():
    try:
        sp.next_track()
        show_command_text("Playing next song on Spotify")
    except Exception as e:
        print(f"Error skipping to next song: {e}")

# Function to show an animation on wake word detection
def show_animation(message):
    animation_label.config(text=message, fg="#00FFFF", font=("Arial", 16))
    animation_label.place(relx=0.5, rely=0.5, anchor="center")
    root.after(2000, lambda: animation_label.place_forget())

# Function to show recognized command text
def show_command_text(command):
    command_label.config(text=f" {command}", fg="#32CD32", font=("Arial", 14, "italic"))
    command_label.place(relx=0.5, rely=0.65, anchor="center")
    root.after(5000, lambda: command_label.place_forget())

# Function to hide all widgets
def hide_all():
    weather_frame.place_forget()
    todo_frame.place_forget()
    reminder_frame.place_forget()
    compliment_frame.place_forget()

# Function to show all widgets
def show_all():
    weather_frame.place(relx=0.95, rely=0.25, anchor="ne")
    todo_frame.place(relx=0.02, rely=0.25, anchor="nw")
    reminder_frame.place(relx=0.02, rely=0.6, anchor="nw")
    compliment_frame.place(relx=0.5, rely=0.95, anchor="s")

def motion_detection():
    cap = cv2.VideoCapture(0)
    first_frame = None
    compliment_update_time = time.time()  # Track the time when the compliment was last updated
    compliment_duration = 30  # Compliment stays constant for 30 seconds
    current_compliment = ""

    global frame
    global res

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            continue

        delta_frame = cv2.absdiff(first_frame, gray)
        thresh_frame = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        contours, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = False

        for contour in contours:
            if cv2.contourArea(contour) < 5000:
                continue
            motion_detected = True
            break

        if motion_detected:
            # Update compliment if the duration has passed or if there's no current compliment
            if time.time() - compliment_update_time > compliment_duration or current_compliment == "":
                # Age and Gender Prediction
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]  # Use the first detected face
                    face_roi = frame[y:y+h, x:x+w]
                    blob = cv2.dnn.blobFromImage(face_roi, 1, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)

                    # Predict gender
                    gender_net.setInput(blob)
                    gender_preds = gender_net.forward()
                    gender_idx = np.argmax(gender_preds)
                    gender = gender_labels[gender_idx]

                    # Predict age
                    age_net.setInput(blob)
                    age_preds = age_net.forward()
                    age_idx = np.argmax(age_preds)
                    age = age_labels[age_idx]

                    # Generate a compliment based on age, gender, and time of day
                    current_hour = time.localtime().tm_hour
                    if current_hour < 12:
                        greeting = "Good morning"
                    elif current_hour < 18:
                        greeting = "Good afternoon"
                    else:
                        greeting = "Good evening"

                    compliments = [
                        "You look fantastic today!",
                        "Your smile is truly contagious!",
                        "You're absolutely glowing!",
                        "Looking sharp as always!",
                        "Your confidence is inspiring!",
                        "You're aging like fine wine!",
                        "You're full of youthful energy!",
                        "Your wisdom shines through!"
                    ]

                    if gender == "Male":
                        specific_compliments = ["Looking sharp!", "You're an inspiration!"]
                    else:
                        specific_compliments = ["You look beautiful!", "You radiate positivity!"]

                    combined_compliments = compliments + specific_compliments
                    current_compliment = f"{greeting}, {gender}! {np.random.choice(combined_compliments)}"
                    compliment_update_time = time.time()  # Update the compliment time

                else:
                    current_compliment = "Hello! Welcome!"

            # Set the compliment text
            compliment_label.config(text=current_compliment)

            # Show all widgets
            show_all()
        else:
            # Hide widgets if no motion is detected
            hide_all()


# Setting up the GUI
root = tk.Tk()
root.title("Smart Mirror")
root.configure(background="black")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())  # Press 'Escape' to exit fullscreen

# Time Label
time_label = tk.Label(root, text="", font=("Arial", 30), fg="white", bg="black")
time_label.place(relx=0.5, rely=0.1, anchor="n")

# Weather Frame
weather_frame = tk.Frame(root, bg="black")
weather_icon_label = tk.Label(weather_frame, bg="black")
weather_icon_label.pack()
weather_label = tk.Label(weather_frame, text="Loading Weather...", font=("Arial", 12), fg="white", bg="black")
weather_label.pack()
weather_frame.place(relx=0.95, rely=0.25, anchor="ne")

# Todo Frame
todo_frame = tk.Frame(root, bg="black")
todo_title = tk.Label(todo_frame, text="TO DO", font=("Arial", 18, "bold"), fg="white", bg="black")
todo_title.pack(anchor="w", padx=10, pady=(0, 10))  
todo_label = tk.Label(todo_frame, text="", font=("Arial", 12), fg="white", bg="black", justify="left")
todo_label.pack(anchor="w", padx=10, pady=(0, 5))  # Add padding below this label
todo_frame.place(relx=0.02, rely=0.25, anchor="nw")

# Reminder Frame
reminder_frame = tk.Frame(root, bg="black")
reminder_title = tk.Label(reminder_frame, text="REMINDERS", font=("Arial", 18, "bold"), fg="white", bg="black")
reminder_title.pack(anchor="w", padx=10, pady=(0, 10))
reminder_label = tk.Label(reminder_frame, text="", font=("Arial", 12), fg="white", bg="black", justify="left")
reminder_label.pack(anchor="w", padx=10, pady=(0,5))
reminder_frame.place(relx=0.02, rely=0.6, anchor="nw")

# Compliment Frame
compliment_frame = tk.Frame(root, bg="black")
compliment_label = tk.Label(compliment_frame, text="", font=("Arial", 12), fg="white", bg="black", justify="center")
compliment_label.pack()
compliment_frame.place(relx=0.5, rely=0.95, anchor="s")

# Animation Label
animation_label = tk.Label(root, text="", font=("Arial", 36, "bold"), bg="black")

# Command Label
command_label = tk.Label(root, text="", font=("Arial", 28, "italic"), bg="black")

# Start the time, weather, sheet data update, and wake word listening threads
update_time()
fetch_weather()
fetch_sheet_data()

# Start motion detection in a separate thread
motion_thread = threading.Thread(target=motion_detection, daemon=True)
motion_thread.start()

# Start wake word listening in a separate thread
wake_word_thread = threading.Thread(target=listen_for_wake_word, daemon=True)
wake_word_thread.start()

# Run the Tkinter event loop
root.mainloop()
