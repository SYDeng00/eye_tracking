# import os
# import pandas as pd
# import re

# def process_csv_files(directory):
#     domain_consistent_gaze, domain_inconsistent_gaze = 0, 0
#     flipped_folders = ['images_5_6', 'images_19_20', 'images_23_24', 'images_29_30', 'images_33_34', 'images_49_50']

#     for root, dirs, files in os.walk(directory):
#         if 'Advertisements' in dirs:
#             dirs.remove('Advertisements')  # Exclude 'Advertisements' folder

#         folder_flipped = any(folder in root for folder in flipped_folders)

#         for file in files:
#             if file.endswith('.csv'):
#                 file_path = os.path.join(root, file)
#                 is_reversed = re.search(r'participant_\d+_reverse_(True|False).csv', file)
#                 reverse_count = False

#                 if is_reversed and is_reversed.group(1) == 'True':
#                     reverse_count = True

#                 try:
#                     df = pd.read_csv(file_path)
#                     df['average_gaze_x'] = (df['gaze_right_eye_x'] + df['gaze_left_eye_x']) / 2
#                     if reverse_count ^ folder_flipped:  # XOR operation to determine actual direction
#                         domain_inconsistent_gaze += (df['average_gaze_x'] > 0.55).sum()
#                         domain_consistent_gaze += (df['average_gaze_x'] <= 0.45).sum()
#                     else:
#                         domain_consistent_gaze += (df['average_gaze_x'] > 0.55).sum()
#                         domain_inconsistent_gaze += (df['average_gaze_x'] <= 0.45).sum()
#                 except Exception as e:
#                     print(f"Error processing file {file_path}: {e}")

#     return domain_consistent_gaze, domain_inconsistent_gaze

# directory_path = 'data'
# results = process_csv_files(directory_path)
# print("Domain consistent gaze:", results[0], "Domain inconsistent gaze:", results[1])


import os
import pandas as pd
import re
from collections import OrderedDict

def process_csv_files(directory):
    data = OrderedDict()
    point_time = 5 / 470 # change point to time 

    flipped_folders = ['images_5_6', 'images_19_20', 'images_23_24', 'images_29_30', 'images_33_34', 'images_49_50']

    for root, dirs, files in os.walk(directory):
        if 'Advertisements' in dirs:
            dirs.remove('Advertisements')  # Exclude 'Advertisements' folder

        folder_flipped = any(folder in root for folder in flipped_folders)

        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                is_reversed = re.search(r'participant_(\d+)_reverse_(True|False).csv', file)
                participant_id = int(is_reversed.group(1)) if is_reversed else 0
                reverse_count = False

                if is_reversed and is_reversed.group(2) == 'True':
                    reverse_count = True

                try:
                    df = pd.read_csv(file_path)
                    df['average_gaze_x'] = (df['gaze_right_eye_x'] + df['gaze_left_eye_x']) / 2
                    domain_consistent_gaze = (df['average_gaze_x'] > 0.55).sum() if reverse_count ^ folder_flipped else (df['average_gaze_x'] <= 0.45).sum()
                    domain_inconsistent_gaze = (df['average_gaze_x'] <= 0.45).sum() if reverse_count ^ folder_flipped else (df['average_gaze_x'] > 0.55).sum()

                    if participant_id not in data:
                        data[participant_id] = {'consistent': 0, 'inconsistent': 0}
                    data[participant_id]['consistent'] += domain_consistent_gaze
                    data[participant_id]['inconsistent'] += domain_inconsistent_gaze

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Convert dictionary to a list of lists for DataFrame

    processed_data = []
    for pid, values in data.items():
        consistent_time = values['consistent'] * point_time
        inconsistent_time = values['inconsistent'] * point_time
        processed_data.append([pid, values['consistent'], values['inconsistent'], consistent_time, inconsistent_time])

    return processed_data

directory_path = 'data'
results = process_csv_files(directory_path)

# Create a DataFrame and save to a CSV file
df_results = pd.DataFrame(results, columns=['Participant', 'Domain Consistent Gaze Points', 'Domain Inconsistent Gaze Points', 'Domain Consistent Gaze Time (s)', 'Domain Inconsistent Gaze Time (s)'])
df_results.sort_values(by='Participant', inplace=True)  # Sort by Participant ID
output_file = 'participants_gaze_data.csv'
df_results.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
