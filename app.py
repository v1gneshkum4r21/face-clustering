from utils import (upload_to_drive_and_send_email, show_cluster_preview, process_uploaded_files, 
                  get_all_clusters, delete_cluster,
                  delete_image_from_cluster, move_image_to_cluster, process_file, email_is_valid, send_cluster_notification)
from database import Database
import streamlit as st
import face_recognition
import os
from pathlib import Path
from PIL import Image
import numpy as np
from encodings_manager import EncodingsManager
from shared_constants import RESULTS_FOLDER, DATASET_FOLDER
from config import ADMIN_PASSWORD
from admin_interface import admin_interface
from datetime import datetime

# Must be first Streamlit command
st.set_page_config(
    page_title="Face Recognition System",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'db' not in st.session_state:
    st.session_state['db'] = Database()

def init_session_state():
    if 'encodings_manager' not in st.session_state:
        st.session_state.encodings_manager = EncodingsManager(RESULTS_FOLDER)
    if 'pending_requests' not in st.session_state:
        st.session_state.pending_requests = []
    if 'processed_clusters' not in st.session_state:
        st.session_state.processed_clusters = set()

def user_interface():
    st.title("Find Your Photos")
    
    tab1, tab2 = st.tabs(["Upload Photo", "Check Request Status"])
    
    with tab1:
        st.subheader("Upload a photo")
        uploaded_file = st.file_uploader(
            "Upload a clear face photo", 
            type=['jpg', 'jpeg', 'png'],
            help="Maximum file size: 200MB"
        )
        
        email = st.text_input(
            "Your email address:",
            key="email_input",
            help="We'll send the matched photos to this address"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Preview", width=300)
            
            if st.button("Submit", disabled=not email):
                handle_upload(uploaded_file, email)
    
    with tab2:
        st.subheader("Check Request Status")
        request_id = st.text_input(
            "Enter your Request ID:",
            help="The ID you received after uploading"
        )
        email_check = st.text_input(
            "Enter your email:",
            help="The email you used for the request"
        )
        
        if st.button("Check Status", disabled=not (request_id and email_check)):
            show_request_status(request_id, email_check)

def handle_upload(uploaded_file, email):
    try:
        # Save uploaded file
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        file_path = temp_dir / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process image
        cluster_id = process_file(str(file_path), st.session_state.encodings_manager)
        
        if cluster_id:
            request_id = f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.db.create_request(
                request_id=request_id,
                email=email,
                cluster_id=cluster_id,
                image_path=str(file_path)
            )
            
            st.success(f"""
            ✅ Photo uploaded successfully!
            Your Request ID: {request_id}
            Please save this ID to check your request status.
            We'll email you when matches are found.
            """)
        else:
            st.error("No face detected in the uploaded image. Please try another photo.")
            
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")
    finally:
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()

def show_request_status(request_id, email):
    try:
        request = st.session_state.db.get_request(request_id, email)
        if request:
            status = request[5]  # Assuming status is at index 5
            if status == 'pending':
                st.info("Your request is still being processed. We'll email you when complete.")
            elif status == 'approved':
                st.success("Your request was approved! Check your email for the matches.")
            elif status == 'rejected':
                st.error("Your request was rejected. Please try uploading a clearer photo.")
        else:
            st.error("Request not found. Please check your Request ID and email.")
    except Exception as e:
        st.error(f"Error checking status: {str(e)}")

def main():
    init_session_state()
    
    # Admin login in sidebar
    if not st.session_state.is_admin:
        with st.sidebar:
            with st.form("admin_login"):
                password = st.text_input("Admin Password", type="password")
                if st.form_submit_button("Login"):
                    if password == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.experimental_rerun()
                    else:
                        st.error("Invalid password")
    
    # Show appropriate interface
    if st.session_state.is_admin:
        admin_interface()
    else:
        user_interface()

if __name__ == "__main__":
    main()