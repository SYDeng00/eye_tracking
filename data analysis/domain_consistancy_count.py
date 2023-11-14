import os
import pandas as pd
import re

def process_csv_files(directory):
    domain_consistent_gaze, domain_inconsistent_gaze = 0, 0
    flipped_folders = ['images_5_6', 'images_19_20', 'images_23_24', 'images_29_30', 'images_33_34', 'images_49_50']

    for root, dirs, files in os.walk(directory):
        if 'Advertisements' in dirs:
            dirs.remove('Advertisements')  # Exclude 'Advertisements' folder

        folder_flipped = any(folder in root for folder in flipped_folders)

        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                is_reversed = re.search(r'participant_\d+_reverse_(True|False).csv', file)
                reverse_count = False

                if is_reversed and is_reversed.group(1) == 'True':
                    reverse_count = True

                try:
                    df = pd.read_csv(file_path)
                    df['average_gaze_x'] = (df['gaze_right_eye_x'] + df['gaze_left_eye_x']) / 2
                    if reverse_count ^ folder_flipped:  # XOR operation to determine actual direction
                        domain_inconsistent_gaze += (df['average_gaze_x'] > 0.5).sum()
                        domain_consistent_gaze += (df['average_gaze_x'] <= 0.5).sum()
                    else:
                        domain_consistent_gaze += (df['average_gaze_x'] > 0.5).sum()
                        domain_inconsistent_gaze += (df['average_gaze_x'] <= 0.5).sum()
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    return domain_consistent_gaze, domain_inconsistent_gaze

directory_path = 'data'
results = process_csv_files(directory_path)
print("Domain consistent gaze:", results[0], "Domain inconsistent gaze:", results[1])
