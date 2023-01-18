import tensorflow as tf
from tensorflow import keras
import h5py
import pynput
import time
from pynput import keyboard
import tkinter as tk
import numpy as np
from tkinter import messagebox, font
from sklearn.metrics import f1_score, precision_score, recall_score
from tkinter import *
import pickle

# Importing the standard_scalar variable to transform new extracted data
with open('x.pickle', 'rb') as handle:
    Standard_Scaler = pickle.load(handle)
# Loading the model
loaded_model = tf.keras.models.load_model(
    'my_model.h5', custom_objects={'get_f1': f1_score})


# Lists to store necessary features
features = []
hold = []
up_down = []
down_down = []
key_press_times = []
key_release_times = []

# A function that record the times of key press


def on_key_press(key):
    key_press_times.append(time.time())

# A function that record the times of key release


def on_key_release(key):
    key_release_times.append(time.time())

# A function that is called on the input field of the password is on focus


def on_password_focus(event):
    global listener, features, hold, up_down, down_down, key_press_times, key_release_times
    # Clearing everything
    features.clear()
    hold.clear()
    up_down.clear()
    down_down.clear()
    key_press_times.clear()
    key_release_times.clear()    
    # Defining a keyboard listener that uses the function of press and release
    listener = keyboard.Listener(
        on_press=on_key_press, on_release=on_key_release)
    listener.start()
    print("started extracting")

# A function that is called when the users presses enter
def on_password_return(event):
    # Waits 2 seconds and stops the listener
    time.sleep(2)
    listener.stop()
    print("DONE")
    global features, hold, up_down, down_down, key_press_times, key_release_times
# Calculating the the necessary features by using the press and release lists
    for i in range(len(key_press_times)):
        # in those if conditions the expected Shift is handled
        if (i == 5):
            hold.append(key_release_times[i+1] - key_press_times[i])
            continue
        if (i == 6):
            up_down.append(key_press_times[i+1] - key_release_times[i])
            down_down.append(key_press_times[i+1] - key_press_times[i-1])
            continue
        hold.append(key_release_times[i] - key_press_times[i])
        if (i != len(key_press_times)-1):
            up_down.append(key_press_times[i+1] - key_release_times[i])
            down_down.append(key_press_times[i+1] - key_press_times[i])
    # adding all features in a one list to use it in prediction
    for i in range(len(hold)):
        if (i == 0):
            features.append(hold[i])
        else:
            features.append(down_down[i-1])
            features.append(up_down[i-1])
            features.append(hold[i-1])
    print(features)
    print(len(features))
# A function that is called after pressing the submit button


def on_submit():
    global features, hold, up_down, down_down
    username.focus_set()
    user = username.get()
    # User names should start with admin and then number  of the user
    # Also the features should be 31 length
    if user[:5] == "admin" and password.get() == ".tie5Ronal" and len(features) == 31:
        # Converting the list to array and applying standardization
        features_arr = np.array(features)
        features_arr = Standard_Scaler.transform(features_arr.reshape(1, -1))
        auth = loaded_model.predict(features_arr)
        print(auth)
        print(np.argmax(auth))
        # Using a 0.75 probability as a thresh hold
        if ((np.argmax(auth) == int(user[5:])) and np.max(auth) > 0.99):
            messagebox.showinfo("Login Successful", "Welcome Admin!")
        else:
            messagebox.showinfo("NOT Authenticated", "Try again!")
    else:
        messagebox.showerror(
            "Login Failed", "Invalid username, password,or order")
    
    username.delete(0, END)
    password.delete(0, END)


root = tk.Tk()
root.geometry("600x600")
root.configure(bg='#87CEFA')
root.title("Login Page")

label_title = tk.Label(root, text="User Authentication using Keystroke dynamics",
                       bg='#87CEFA', font=("Helvetica", 20))
label_title.pack(pady=20)

label_username = tk.Label(root, text="Username:",
                          bg='#87CEFA', font=("Helvetica", 14))
label_username.pack(pady=10)
username = tk.Entry(root, font=("Helvetica", 14))
username.pack(pady=10)

label_password = tk.Label(root, text="Password:",
                          bg='#87CEFA', font=("Helvetica", 14))
label_password.pack(pady=10)
password = tk.Entry(root, font=("Helvetica", 14))
password.pack(pady=10)
password.bind("<FocusIn>", on_password_focus)
password.bind("<Return>", on_password_return)


submit_btn = tk.Button(root, text="Submit", font=(
    "Helvetica", 14), command=on_submit)
submit_btn.pack(pady=10)


root.mainloop()
