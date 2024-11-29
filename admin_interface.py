import streamlit as st
import os
from pathlib import Path
from stages.process_image import process_file
from utils import (
    delete_image_from_cluster,
    move_image_to_cluster,
    show_cluster_preview,
    show_system_stats,
    process_uploaded_files,
    get_all_clusters,
    upload_to_drive_and_send_email,
    rename_cluster,
    delete_cluster
)
from shared_constants import DATASET_FOLDER, RESULTS_FOLDER
from crud_operations import find_cluster_by_image, show_cluster_images
from database import Database
from datetime import datetime
from PIL import Image
import time
import shutil

# Initialize database
db = Database()

def admin_interface():
    st.title("Admin Dashboard")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Process Images", "Manage Clusters", "User Requests", "System Stats"]
    )
    
    if page == "Process Images":
        show_processing_interface()
    elif page == "Manage Clusters":
        show_cluster_management()
    elif page == "User Requests":
        show_user_requests()
    else:
        show_stats_interface()

def show_stats_interface():
    stats = show_system_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Clusters", stats.get('total_clusters', 0))
    with col2:
        st.metric("Total Images", stats.get('total_images', 0))
    with col3:
        st.metric("Storage Used (MB)", f"{stats.get('storage_used', 0):.2f}")

def show_processing_interface():
    st.header("Process New Images")
    uploaded_files = st.file_uploader("Upload Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    
    if uploaded_files:
        processed_files = process_uploaded_files(uploaded_files)
        with st.spinner('Processing images...'):
            for filepath in processed_files:
                cluster_id = process_file(filepath, st.session_state.encodings_manager)
                if cluster_id:
                    st.success(f"Image processed and added to cluster {cluster_id}")
                else:
                    st.warning(f"No face detected in {filepath.name}")
                os.remove(filepath)  # Cleanup temp file

def show_cluster_management():
    st.header("Cluster Management")
    
    if st.button("🔄 Refresh Clusters"):
        st.experimental_rerun()
    
    clusters = get_all_clusters()
    
    if not clusters:
        st.info("No clusters found")
        return
    
    for cluster in clusters:
        cluster_id = cluster['id']
        
        # Create a row for cluster actions
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Add rename input field
            new_name = st.text_input(
                "New name",
                value=cluster_id,
                key=f"rename_{cluster_id}"
            )
        
        with col2:
            # Add rename button
            if st.button("Rename", key=f"btn_rename_{cluster_id}"):
                if new_name != cluster_id:
                    success, message = rename_cluster(cluster_id, new_name)
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
        
        with col3:
            # Add delete button with confirmation
            if st.button("🗑️ Delete", key=f"btn_delete_{cluster_id}"):
                st.warning(f"Are you sure you want to delete cluster {cluster_id}?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes", key=f"confirm_delete_{cluster_id}"):
                        success, message = delete_cluster(cluster_id)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
                with col_no:
                    if st.button("No", key=f"cancel_delete_{cluster_id}"):
                        st.experimental_rerun()
        
        # Show cluster contents in expander
        with st.expander(f"Cluster {cluster_id} ({cluster['image_count']} images)"):
            images = show_cluster_preview(cluster_id)
            
            if not images:
                st.info("No images in this cluster")
                continue
            
            # Create a grid layout for images
            cols = st.columns(4)
            for idx, (img_name, img) in enumerate(images):
                with cols[idx % 4]:
                    st.image(img, caption=img_name, use_column_width=True)
                    
                    # Image action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            "Delete",
                            key=f"del_{cluster_id}_{idx}_{img_name}"
                        ):
                            if delete_image_from_cluster(cluster_id, img_name):
                                st.success(f"Deleted {img_name}")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to delete image")
                    
                    with col2:
                        other_clusters = [c['id'] for c in clusters if c['id'] != cluster_id]
                        if other_clusters:
                            target_cluster = st.selectbox(
                                "Move to",
                                other_clusters,
                                key=f"move_{cluster_id}_{idx}_{img_name}"
                            )
                            if st.button(
                                "Move",
                                key=f"btn_move_{cluster_id}_{idx}_{img_name}"
                            ):
                                if move_image_to_cluster(cluster_id, target_cluster, img_name):
                                    st.success(f"Moved {img_name} to {target_cluster}")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to move image")

def show_user_requests():
    if not hasattr(st.session_state, 'db'):
        st.error("Database not initialized")
        return
        
    st.header("User Requests")
    tab1, tab2 = st.tabs(["Pending Requests", "All Requests"])
    
    with tab1:
        show_pending_requests()
    with tab2:
        show_all_requests()

def show_pending_requests():
    pending_requests = db.get_pending_requests()
    if not pending_requests:
        st.info("No pending requests")
        return
        
    for request in pending_requests:
        with st.expander(f"Request: {request[0]}"):
            cols = st.columns([2, 1])
            
            with cols[0]:
                st.text(f"Email: {request[1]}")
                st.text(f"Cluster ID: {request[2]}")
                st.text(f"Submitted: {request[4]}")
                
                cluster_path = Path(RESULTS_FOLDER) / str(request[2])
                if cluster_path.exists():
                    show_cluster_images(cluster_path)
            
            with cols[1]:
                if st.button("Approve", key=f"approve_{request[0]}"):
                    if handle_request_approval(request[0]):
                        st.experimental_rerun()
                if st.button("Reject", key=f"reject_{request[0]}"):
                    db.update_request_status(request[0], 'rejected')
                    st.experimental_rerun()

def show_all_requests():
    all_requests = db.get_all_requests()
    if not all_requests:
        st.info("No requests found")
        return
        
    for request in all_requests:
        with st.expander(f"Request: {request[0]} ({request[5]})"):
            st.text(f"Email: {request[1]}")
            st.text(f"Cluster ID: {request[2]}")
            st.text(f"Submitted: {request[4]}")
            st.text(f"Status: {request[5]}")

def handle_request_approval(request_id):
    request = db.get_request_by_id(request_id)
    if not request:
        st.error("Request not found")
        return False
        
    email = request[1]
    cluster_id = request[2]
    
    success, message = upload_to_drive_and_send_email(email, cluster_id)
    if success:
        db.update_request_status(request_id, 'approved')
        st.success("Request approved and email sent successfully!")
        return True
    else:
        st.error(f"Failed to process request: {message}")
        return False

if __name__ == "__main__":
    admin_interface()