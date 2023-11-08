import io
import sys
import time
import os
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import tobii_research as tr
from PIL import Image
import webbrowser
import random

sg.theme("DarkBlue")
sg.set_options(font=("Courier New", 32))

survey_url = 'https://www.wjx.cn/vm/Qi175TV.aspx#'

## Find eyetracker
et = tr.find_all_eyetrackers()[0]

participant_id = 4
## Apply license file
license_file = "license_key_00395217_-_DTU_Compute_IS404-100106341184"

if license_file != "":
    with open(license_file, "rb") as f:
        license = f.read()
        res = et.apply_licenses(license)
        if len(res) != 0:
            print(
                "Failed to apply license from single key. Validation result: %s."
                % (res[0].validation_result)
            )
            exit
else:
    print("No license file installed")

def gaze_data_callback(gaze_data):
    d["gaze_left_eye"].append(gaze_data["left_gaze_point_on_display_area"])
    d["gaze_right_eye"].append(gaze_data["right_gaze_point_on_display_area"])

# Display resolution is below
layout = [
    [
        sg.Graph(
            canvas_size=(2560, 1440),
            graph_bottom_left=(0, 0),
            graph_top_right=(2560, 1440),
            background_color="black",
            key="graph",
            enable_events=True,
            drag_submits=True,
        )
    ],
]
window = sg.Window("Title", layout, finalize=True, return_keyboard_events=True)

window.maximize()

def resize_image_to_half_screen(image):

    # Resize the image to the target dimensions
    return image.resize((int(700), int(600)))

def draw_images(slide_number, graph, reverse):
    if reverse:
            indices = range(slide_number + 1, slide_number - 1, -1)
    else:
            indices = range(slide_number, slide_number + 2)
            
    for i, loc in zip(indices, [ (290, 1140), (1570, 1140)]):  # Only loop twice and adjust locations
        image = Image.open(f"./Data/Advertisement/{i}.PNG")
        image = resize_image_to_half_screen(image)
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        graph.DrawImage(data=bio.getvalue(), location=loc)

def draw_fixation_cross():
    graph.draw_line((2560 / 2, 1440 / 2 - 50), (2560 / 2, 1440 / 2 + 50), width=5, color="white")
    graph.draw_line((2560 / 2 - 50, 1440 / 2), (2560 / 2 + 50, 1440 / 2), width=5, color="white")

graph = window["graph"]

number_photo = 60
pairs = list(range(1, number_photo+1, 2))
selected_numbers = []
survey_count = 1

graph.draw_text(""" 
                    Thank you for participating in our experiment\n\n
                    This test will consist of 30 slides with 2 images side by side that will be displayed for 5 seconds.
                    You're goal is to be able to recall as many brands as possible.
                    You continue to the next set of images by pressing spacebar.
                    Before the slide a white focus cross will apeare for 1 second.
                    Please look at the cross to center your vision.\n\n
                    Press spacebar to start
                """
                    , (2560 / 2 , 1440/2 +200), color='white', font='Any 36')

while True:
    event, values = window.read()
    if event == " " or sg.WINDOW_CLOSED:
        graph.erase()
        break

while pairs:

    graph.draw_text("Press space to continue", (2560 / 2 , 1440/2 +200), color='white', font='Any 24')
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    elif event == " ":
        slide_number = random.choice(pairs)
        selected_numbers.append(slide_number)

        print("event space")
        graph.erase()
        draw_fixation_cross()
        window.refresh()
        time.sleep(1)
        graph.erase()
        d = {"gaze_left_eye": [], "gaze_right_eye": []}
        et.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

        reverse = random.choice([True, False])  
        draw_images(slide_number, graph, reverse)

        window.refresh()
        time.sleep(5)
        et.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        graph.erase()
        window.refresh()

        df = pd.DataFrame.from_dict(d)
        df["gaze_left_eye_x"] = [x[0] for x in df["gaze_left_eye"].values]
        df["gaze_left_eye_y"] = [x[1] for x in df["gaze_left_eye"].values] 
        df["gaze_right_eye_x"] = [x[0] for x in df["gaze_right_eye"].values]
        df["gaze_right_eye_y"] = [x[1] for x in df["gaze_right_eye"].values]

        file_path = f"./Data/{slide_number}/{participant_id}-data-{str(reverse)}.csv"
        directory = os.path.dirname(file_path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(file_path):
            os.remove(file_path)

        df.to_csv(file_path)

        print(slide_number)

        survey_count += 1

        print(selected_numbers)
        pairs.remove(slide_number)
        print("Pairs after removal:", pairs)

order_numebr_path = f"./Data/Advertisement/order/{participant_id}-order.txt"
directory2 = os.path.dirname(order_numebr_path)

if not os.path.exists(directory2):
    os.makedirs(directory2)

if os.path.exists(order_numebr_path):
    os.remove(file_path)

with open(order_numebr_path, 'w') as file:
    print(selected_numbers)
    for i, number in enumerate(selected_numbers, start=1):  
        if i % 5 == 0:  
            file.write(f"{number}\n")
        else:
            file.write(f"{number}\t")  

webbrowser.open(survey_url)
window.close()
