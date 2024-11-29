import streamlit as st
from pathlib import Path
import face_recognition
import numpy as np
from shared_constants import RESULTS_FOLDER
from utils.core import move_image_to_cluster, delete_cluster

def analyze_clusters():
    """Analyze existing clusters for potential merging opportunities"""
    st.title("Cluster Analysis")
    
    clusters_path = Path(RESULTS_FOLDER)
    if not clusters_path.exists():
        st.error("Results folder not found")
        return
        
    clusters = [c for c in clusters_path.glob('cluster_*') if c.is_dir()]
    if not clusters:
        st.info("No clusters found for analysis")
        return
        
    st.subheader("Cluster Similarity Analysis")
    
    # Analyze each cluster pair
    with st.spinner("Analyzing clusters..."):
        similar_clusters = []
        
        for i, cluster1 in enumerate(clusters):
            for cluster2 in clusters[i+1:]:
                similarity = compare_clusters(cluster1, cluster2)
                if similarity['score'] > 0.7:  # High similarity threshold
                    similar_clusters.append({
                        'cluster1': cluster1.name,
                        'cluster2': cluster2.name,
                        'similarity': similarity
                    })
        
        if similar_clusters:
            st.warning(f"Found {len(similar_clusters)} potential cluster pairs that could be merged")
            
            for pair in similar_clusters:
                with st.expander(f"Similarity: {pair['cluster1']} ↔️ {pair['cluster2']}"):
                    st.write(f"Similarity Score: {pair['similarity']['score']:.2f}")
                    st.write(f"Matching Faces: {pair['similarity']['matching_faces']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Merge {pair['cluster1']} → {pair['cluster2']}", 
                                   key=f"merge_{pair['cluster1']}_{pair['cluster2']}"):
                            merge_clusters(pair['cluster1'], pair['cluster2'])
                            st.success("Clusters merged successfully!")
                            st.experimental_rerun()
                    
                    with col2:
                        if st.button("View Details", key=f"details_{pair['cluster1']}_{pair['cluster2']}"):
                            show_cluster_comparison(pair['cluster1'], pair['cluster2'])
        else:
            st.success("No highly similar clusters found")

def merge_clusters(source_cluster, target_cluster):
    """Merge source cluster into target cluster"""
    try:
        source_path = Path(RESULTS_FOLDER) / source_cluster
        
        # Move all images from source to target
        for img_path in source_path.glob('*.{jpg,jpeg,png,JPG,JPEG,PNG}'):
            move_image_to_cluster(source_cluster, target_cluster, img_path.name)
        
        # Delete source cluster
        delete_cluster(source_cluster)
        return True
        
    except Exception as e:
        st.error(f"Error merging clusters: {str(e)}")
        return False

def compare_clusters(cluster1_path, cluster2_path):
    """Compare two clusters and return similarity metrics"""
    try:
        # Get face encodings from both clusters
        encodings1 = get_cluster_encodings(cluster1_path)
        encodings2 = get_cluster_encodings(cluster2_path)
        
        if not encodings1 or not encodings2:
            return {'score': 0, 'matching_faces': 0}
            
        # Compare each face encoding
        matches = 0
        total_comparisons = len(encodings1) * len(encodings2)
        
        for enc1 in encodings1:
            for enc2 in encodings2:
                if face_recognition.compare_faces([enc1], enc2, tolerance=0.6)[0]:
                    matches += 1
                    
        similarity_score = matches / total_comparisons if total_comparisons > 0 else 0
        
        return {
            'score': similarity_score,
            'matching_faces': matches,
            'total_faces': (len(encodings1), len(encodings2))
        }
        
    except Exception as e:
        print(f"Error comparing clusters: {str(e)}")
        return {'score': 0, 'matching_faces': 0, 'total_faces': (0, 0)}

def get_cluster_encodings(cluster_path):
    """Get face encodings for all images in a cluster"""
    encodings = []
    
    for img_path in cluster_path.glob('*.{jpg,jpeg,png,JPG,JPEG,PNG}'):
        try:
            image = face_recognition.load_image_file(str(img_path))
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                encodings.append(face_encodings[0])
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
            
    return encodings

def show_cluster_comparison(cluster1_id, cluster2_id):
    """Show detailed comparison between two clusters"""
    st.subheader(f"Comparing {cluster1_id} with {cluster2_id}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"### {cluster1_id}")
        cluster1_path = Path(RESULTS_FOLDER) / cluster1_id
        show_cluster_images(cluster1_path)
        
    with col2:
        st.write(f"### {cluster2_id}")
        cluster2_path = Path(RESULTS_FOLDER) / cluster2_id
        show_cluster_images(cluster2_path)

def show_cluster_images(cluster_path):
    """Display images from a cluster"""
    images = []
    for img_path in cluster_path.glob('*.{jpg,jpeg,png,JPG,JPEG,PNG}'):
        try:
            img = face_recognition.load_image_file(str(img_path))
            images.append((img_path.name, img))
        except Exception as e:
            print(f"Error loading {img_path}: {str(e)}")
    
    for name, img in images:
        st.image(img, caption=name, use_column_width=True)