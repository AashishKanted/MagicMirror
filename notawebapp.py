import tkinter as tk
import time
import threading
import requests
import json
import speech_recognition as sr
from PIL import Image, ImageTk
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Placeholder for your Google Sheets API key, Sheet ID, and OpenWeatherMap API key
SHEET_ID = '12RAcvir3adNOZikeLpR35oprVppqx9aKzujgmbxBCHo'
API_KEY = 'AIzaSyCg1F3hUA8cri7HHtvLiOwsfCxvbp4czfQ'
RANGE = 'Sheet2'

WEATHER_API_KEY = "89c783ca6ca15a47906557128fbce8ec"
CITY = "Goa"


SPOTIPY_CLIENT_ID = '4b4d7267b1bf47adae77bf7c4debd80a'
SPOTIPY_CLIENT_SECRET = '199b93b8982f435b9e6d962255000088'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-playback-state,user-modify-playback-state'

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

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

    root.after(60000, fetch_weather)  # Update weather every 60 seconds

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
    else:
        print("Command not recognized.")

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
    weather_frame.place(relx=0.95, rely=0.05, anchor="ne")
    todo_frame.place(relx=0.02, rely=0.05, anchor="nw")
    reminder_frame.place(relx=0.02, rely=0.35, anchor="nw")
    compliment_frame.place(relx=0.5, rely=0.95, anchor="s")

# Setting up the GUI
root = tk.Tk()
root.title("Smart Mirror - Aurora")
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
todo_title.pack(anchor="w", padx=10)
todo_label = tk.Label(todo_frame, text="", font=("Arial", 12), fg="white", bg="black", justify="left")
todo_label.pack(anchor="w", padx=10)
todo_frame.place(relx=0.02, rely=0.25, anchor="nw")

# Reminder Frame
reminder_frame = tk.Frame(root, bg="black")
reminder_title = tk.Label(reminder_frame, text="REMINDERS", font=("Arial", 18, "bold"), fg="white", bg="black")
reminder_title.pack(anchor="w", padx=10)
reminder_label = tk.Label(reminder_frame, text="", font=("Arial", 12), fg="white", bg="black", justify="left")
reminder_label.pack(anchor="w", padx=10)
reminder_frame.place(relx=0.02, rely=0.6, anchor="nw")

# Compliment Frame
compliment_frame = tk.Frame(root, bg="black")
compliment_label = tk.Label(compliment_frame, text="* Insert more F L I R T S *", font=("Arial", 12), fg="white", bg="black", justify="center")
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

# Start wake word listening in a separate thread
wake_word_thread = threading.Thread(target=listen_for_wake_word, daemon=True)
wake_word_thread.start()

# Run the Tkinter event loop
root.mainloop()
