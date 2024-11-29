import face_recognition
import os
from pathlib import Path
from shutil import copyfile
from utils import save_encodings
from shared_constants import RESULTS_FOLDER
        
cwd = os.getcwd()
results_path = os.path.join(cwd, 'results')
encodings = {}

def process_file(filepath, encodings_manager):
    try:
        print(f"Processing file: {filepath}")
        img = face_recognition.load_image_file(filepath)
        fe = face_recognition.face_encodings(img)
        
        if not fe:
            print("No face detected in image")
            return None
            
        fe = fe[0]
        action_taken = False
        curr_image_cluster_id = None
        tolerance = 0.6
        
        for cluster_id, cluster_encodings in encodings_manager.encodings.items():
            for encoding in cluster_encodings:
                distance = face_recognition.face_distance([encoding], fe)[0]
                if distance < tolerance:
                    print(f"Match found in cluster {cluster_id} with distance {distance}")
                    curr_image_cluster_id = cluster_id
                    encodings_manager.encodings[cluster_id].append(fe)
                    action_taken = True
                    break
            if action_taken:
                break
                
        if not action_taken:
            curr_image_cluster_id = f"cluster_{len(encodings_manager.encodings.keys()) + 1}"
            print(f"Creating new cluster {curr_image_cluster_id}")
            encodings_manager.encodings[curr_image_cluster_id] = [fe]
        
        # Use RESULTS_FOLDER instead of results_path
        cluster_dir = Path(RESULTS_FOLDER) / curr_image_cluster_id
        cluster_dir.mkdir(exist_ok=True, parents=True)
        print(f"Created/verified cluster directory: {cluster_dir}")
        
        # Copy image to cluster directory
        dest_path = cluster_dir / Path(filepath).name
        print(f"About to copy file:")
        print(f"Source exists: {Path(filepath).exists()}")
        print(f"Source path: {filepath}")
        print(f"Destination path: {dest_path}")
        copyfile(filepath, dest_path)
        print(f"File copied successfully. Destination exists: {dest_path.exists()}")
        
        encodings_manager.save_encodings()
        return curr_image_cluster_id
        
    except Exception as e:
        print(f"Error processing file {filepath}: {str(e)}")
        return None