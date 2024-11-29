import streamlit as st
import face_recognition
import os
from pathlib import Path
from PIL import Image
from shared_constants import RESULTS_FOLDER

def find_cluster_by_image(image_path, encodings_manager):
    try:
        target_image = face_recognition.load_image_file(image_path)
        target_encodings = face_recognition.face_encodings(target_image)
        
        if not target_encodings:
            st.warning("⚠️ No face detected in the uploaded image")
            return None
            
        target_encoding = target_encodings[0]
        best_match = None
        best_distance = float('inf')
        tolerance = 0.6
        
        for cluster_id, cluster_encodings in encodings_manager.encodings.items():
            for encoding in cluster_encodings:
                distance = face_recognition.face_distance([encoding], target_encoding)[0]
                if distance < tolerance and distance < best_distance:
                    best_distance = distance
                    best_match = cluster_id
        
        return best_match
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def show_cluster_images(cluster_path):
    images = []
    for img_path in Path(cluster_path).glob('*.jpg'):
        try:
            img = Image.open(img_path)
            images.append((img, img_path.name))
        except Exception as e:
            st.warning(f"Could not load {img_path.name}: {str(e)}")
    
    cols = st.columns(4)
    for idx, (img, name) in enumerate(images):
        with cols[idx % 4]:
            st.image(img, caption=name, use_column_width=True)

def find_face_page():
    st.header("Find Face Cluster")
    
    results_folder = RESULTS_FOLDER
    
    uploaded_file = st.file_uploader("Upload a face image to find its cluster", 
                                   type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        # Save temporary file
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Show uploaded image
            st.subheader("Uploaded Image:")
            st.image(temp_path, width=200)
            
            cluster_name = find_cluster_by_image(temp_path, results_folder)
            
            if cluster_name:
                st.success(f"Face found in cluster: {cluster_name}")
                
                # Show all images from the cluster
                st.subheader("Cluster Images:")
                cluster_path = os.path.join(results_folder, cluster_name)
                show_cluster_images(cluster_path)
            else:
                st.warning("Face not found in any existing cluster")
        
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    find_face_page()
