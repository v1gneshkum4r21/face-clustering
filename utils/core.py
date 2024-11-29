import os
from pathlib import Path
from PIL import Image
from shared_constants import RESULTS_FOLDER
import shutil
import pickle
import re

def delete_image_from_cluster(cluster_id, image_name):
    try:
        image_path = Path(RESULTS_FOLDER) / str(cluster_id) / image_name
        if image_path.exists():
            image_path.unlink()
        return True
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False

def move_image_to_cluster(source_cluster, target_cluster, image_name):
    try:
        source_path = Path(RESULTS_FOLDER) / str(source_cluster) / image_name
        target_path = Path(RESULTS_FOLDER) / str(target_cluster) / image_name
        
        if source_path.exists():
            target_path.parent.mkdir(exist_ok=True)
            source_path.rename(target_path)
        return True
    except Exception as e:
        print(f"Error moving image: {str(e)}")
        return False

def show_cluster_preview(cluster_id):
    cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
    print(f"Looking for images in: {cluster_path}")
    print(f"Path exists: {cluster_path.exists()}")
    
    if not cluster_path.exists():
        return []
    
    images = set()  # Use a set to prevent duplicates
    # Check for files with individual patterns
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        for img_path in cluster_path.glob(ext):
            try:
                img = Image.open(img_path)
                images.add((img_path.name, img))
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
    
    print(f"Total unique images found: {len(images)}")
    print("All files in directory:", list(cluster_path.iterdir()))
    return sorted(list(images))  # Convert back to sorted list for consistent ordering

def process_uploaded_files(files):
    processed_files = []
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    for file in files:
        temp_path = temp_dir / file.name
        try:
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            processed_files.append(temp_path)
        except Exception as e:
            print(f"Error processing {file.name}: {e}")
    
    return processed_files

def get_all_clusters():
    clusters = []
    results_path = Path(RESULTS_FOLDER)
    
    if results_path.exists():
        for cluster_dir in results_path.glob('cluster_*'):
            if cluster_dir.is_dir():
                image_count = len(list(cluster_dir.glob('*.{jpg,jpeg,png}')))
                clusters.append({
                    'id': cluster_dir.name,
                    'image_count': image_count
                })
    
    return clusters

def delete_cluster(cluster_id):
    try:
        cluster_path = Path(RESULTS_FOLDER) / str(cluster_id)
        if cluster_path.exists():
            shutil.rmtree(cluster_path)
            return True, "Cluster deleted successfully"
        return False, "Cluster not found"
    except Exception as e:
        print(f"Error deleting cluster: {str(e)}")
        return False, str(e)

def save_encodings(encodings_dict, file_path):
    """Save face encodings to a file"""
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(encodings_dict, f)
        return True
    except Exception as e:
        print(f"Error saving encodings: {str(e)}")
        return False

def email_is_valid(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def rename_cluster(cluster_id, new_name):
    try:
        old_path = Path(RESULTS_FOLDER) / str(cluster_id)
        new_path = Path(RESULTS_FOLDER) / str(new_name)
        
        if not old_path.exists():
            return False, "Cluster not found"
            
        if new_path.exists():
            return False, "New cluster name already exists"
            
        old_path.rename(new_path)
        return True, "Cluster renamed successfully"
    except Exception as e:
        print(f"Error renaming cluster: {str(e)}")
        return False, str(e)