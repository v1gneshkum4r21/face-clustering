from stages.process_image import process_file

import face_recognition
import os
from pathlib import Path
from shutil import copyfile
from shared_constants import DATASET_FOLDER, RESULTS_FOLDER
from encodings_manager import EncodingsManager

def main():
    encodings_manager = EncodingsManager(RESULTS_FOLDER)
    dataset_path = Path(DATASET_FOLDER)
    
    # Process all images in dataset folder
    for subdir, dirs, files in os.walk(dataset_path):
        total = len(files)
        for idx, file in enumerate(files, 1):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(subdir, file)
                print(f"Processing file {idx}/{total}: {filepath}")
                
                try:
                    # Process the image and get cluster ID
                    cluster_id = process_file(filepath, encodings_manager)
                    
                    if cluster_id:
                        # Copy file to appropriate cluster directory
                        cluster_dir = Path(RESULTS_FOLDER) / cluster_id
                        cluster_dir.mkdir(parents=True, exist_ok=True)
                        copyfile(filepath, cluster_dir / file)
                        print(f"Added to cluster: {cluster_id}")
                    else:
                        print("No face detected, skipping...")
                        
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")

    print(f"Processing complete. Found {len(encodings_manager.encodings)} distinct faces.")

if __name__ == "__main__":
    main()
