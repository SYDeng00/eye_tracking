import os
import pandas as pd
import re
from collections import defaultdict

def process_csv_files(directory):
    data = defaultdict(lambda: defaultdict(int))  # Defaultdict for image group data

    flipped_folders = ['images_5_6', 'images_19_20', 'images_23_24', 'images_29_30', 'images_33_34', 'images_49_50']

    for root, dirs, files in os.walk(directory):
        if 'Advertisements' in dirs:
            dirs.remove('Advertisements')  # Exclude 'Advertisements' folder

        folder_flipped = any(folder in root for folder in flipped_folders)

        # Assuming the last folder name is the image group identifier
        image_group = int(re.findall(r'\d+', os.path.basename(root))[-1]) if re.findall(r'\d+', os.path.basename(root)) else None

        if image_group:  # Only process if image_group is found
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    is_reversed = re.search(r'participant_(\d+)_reverse_(True|False).csv', file)
                    participant_id, reverse_count = (int(is_reversed.group(1)), is_reversed.group(2) == 'True') if is_reversed else (0, False)

                    try:
                        df = pd.read_csv(file_path)
                        df['average_gaze_x'] = (df['gaze_right_eye_x'] + df['gaze_left_eye_x']) / 2
                        domain_consistent_gaze = (df['average_gaze_x'] > 0.55).sum() if reverse_count ^ folder_flipped else (df['average_gaze_x'] <= 0.45).sum()
                        domain_inconsistent_gaze = (df['average_gaze_x'] <= 0.45).sum() if reverse_count ^ folder_flipped else (df['average_gaze_x'] > 0.55).sum()

                        # Assign 1 for consistent and 0 for inconsistent
                        data[image_group][participant_id] = 1 if domain_consistent_gaze > domain_inconsistent_gaze else 0

                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

    return data

directory_path = 'data'
data = process_csv_files(directory_path)

# Convert data to a list of lists for DataFrame
participant_ids = sorted({participant for groups in data.values() for participant in groups})
columns = ['Image Group'] + [f'Participant {pid}' for pid in participant_ids]
processed_data = [[image_group] + [data[image_group][participant] for participant in participant_ids] for image_group in sorted(data)]

# Create a DataFrame and save to a CSV file
df_results = pd.DataFrame(processed_data, columns=columns)
output_file = 'participants_gaze_analysis.csv'
df_results.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
