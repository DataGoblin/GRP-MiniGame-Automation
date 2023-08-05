from mss import mss
import sys
import os
import win32gui
import cv2
import numpy as np
import pickle
import pyautogui
import time
import pydirectinput
from tkinter import Tk, Button
from tkinter import font
import threading

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def find_window_by_keyword(keyword):
    # Function to be called for each window
    def enum_windows_callback(handle, data):
        window_title = win32gui.GetWindowText(handle)
        if keyword.lower() in window_title.lower():
            data.append(handle)
    
    # Get the handles of all windows that match the keyword
    window_handles = []
    win32gui.EnumWindows(enum_windows_callback, window_handles)
    
    if len(window_handles) == 0:
        raise Exception(f'Window not found for keyword: {keyword}')
    
    return window_handles[0]


def get_window_location(window_handle):
    window_rect = win32gui.GetWindowRect(window_handle)
    return  {"top": window_rect[1], "left": window_rect[0], "width": window_rect[2] - window_rect[0], "height": window_rect[3] - window_rect[1]}
 
 
# preloading number binary template dict
templates = []
with open(resource_path("number_data.pkl"), 'rb') as fp:
    templates = pickle.load(fp)


def template_matching(thresholded_frame):
    if np.any(thresholded_frame == 255):
        recognized_number = None
        max_correlation = float('-inf')
        for number, template in templates.items():
            result = cv2.matchTemplate(thresholded_frame, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > max_correlation:
                max_correlation = max_val
                recognized_number = number
        return recognized_number
    else:
        return 0


def start_loop(control_dict):
    # searchs for window by keyword and gets its location
    window_keyword = "Redm"
    window_handle = find_window_by_keyword(window_keyword)
    location = get_window_location(window_handle)

    # variables used for deciding when to send keystroke
    prev_contour_count = 0
    tracking_contours = False
    identified_number = None

    with mss() as sct:
        start_time = time.time()
        while control_dict['running']:

            # Capture the content of the window
            sct_img = sct.grab(location)
            frame = np.array(sct_img)

            # Crop a square in the middle of the frame (20% of the total size)
            # allows various resolutions rather than hard keying crop coords
            height, width, _ = frame.shape
            crop_size = int(min(height, width) * 0.20)
            start_x = (width - crop_size) // 2
            start_y = (height - crop_size) // 2
            cropped_frame = frame[start_y:start_y+crop_size, start_x:start_x+crop_size]

            # crops an extra 30% from the top of the frame
            crop_height = int(cropped_frame.shape[0] * 0.30)
            cropped_frame = cropped_frame[crop_height:, :]

            # very basic logic of when to press /space/ to repeat the minigame. presses every 5 seconds
            if time.time() - start_time >= 5:
                pydirectinput.press('space')
                start_time = time.time()

            # Apply color threshold for bright white pixels
            threshold_value = 250
            _, thresholded_frame = cv2.threshold(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY), threshold_value, 255, cv2.THRESH_BINARY)

            # finds all contours and filters out micro contours
            min_contour_area = 30
            contours, _ = cv2.findContours(thresholded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > min_contour_area]
            contour_count = len(filtered_contours)

            # Trys to identify number if there are white pixels in the frame. Lazy logic but works
            if np.any(thresholded_frame == 255):   
                identified_number = template_matching(thresholded_frame)
                tracking_contours = True

            # Detecting interception based on contour count drop
            if tracking_contours and prev_contour_count != 0 and identified_number != 0 and contour_count < prev_contour_count:
                pyautogui.press(identified_number)
                print(f"Intercepted - Identified Number: {identified_number}")
                tracking_contours = False
                identified_number = None

            prev_contour_count = contour_count

control_dict = {'running': False}

# tkinter gui code. very basic stop/start button
def toggle():
    if control_dict['running']:
        control_dict['running'] = False
        toggle_button.config(text="Start", bg="green")  # Change the button text to "Start" and background to green
    else:
        control_dict['running'] = True
        loop_thread = threading.Thread(target=start_loop, args=(control_dict,))
        loop_thread.start()
        toggle_button.config(text="Stop", bg="red")    # Change the button text to "Stop" and background to red

# Creating the GUI window
root = Tk()
root.title("Marvelous")
root.geometry("200x200")

# Define a custom font
custom_font = font.Font(family="Helvetica", size=14, weight="bold")

# Adding a toggle button with custom styling
toggle_button = Button(root, text="Start", command=toggle,
                       font=custom_font,
                       fg="white",
                       bg="green",
                       borderwidth=2,
                       relief="ridge")

# Center the button in the window
toggle_button.place(x=100, y=100, anchor="center")

# Running the GUI
root.mainloop()