 Face Clustering Application

A Python application that clusters similar faces from images using face recognition and provides Google Drive integration for sharing results.

 Features

- Face detection and recognition using face_recognition library
- Automatic clustering of similar faces
- Google Drive integration for sharing results
- Email notifications when clusters are ready
- Web interface for managing clusters
- Support for multiple image formats (JPG, JPEG, PNG)

 Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Gmail account (for notifications)

 Installation

1. Clone the repository:

git clone <repository-url>

cd face-clustering

2. Install dependencies:

pip install -r requirements.txt

3. Set up Google Cloud credentials:
   - Create a project in Google Cloud Console
   - Enable Drive API and Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials.json and place in project root

4. Create a `.env` file with the following:
env
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
SMTP_USERNAME=your_gmail
SMTP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

 Usage

1. Start the application:

streamlit run app.py

2. Upload images through the web interface

3. The application will:
   - Detect faces in uploaded images
   - Create clusters of similar faces
   - Save images to appropriate clusters
   - Allow uploading clusters to Google Drive
   - Send email notifications with sharing links

 Project Structure

- `/stages` - Processing pipeline stages
- `/utils` - Utility functions and services
- `/results` - Clustered images output
- `/temp_uploads` - Temporary storage for uploads

 API Reference

 Core Functions

- `process_file(filepath, encodings_manager)`: Process single image file
- `upload_to_drive_and_send_email(to_email, cluster_id)`: Share cluster and notify
- `get_all_clusters()`: List all face clusters
- `delete_cluster(cluster_id)`: Remove a cluster

 Utility Services

- Google Drive integration
- Gmail notification service
- SMTP email service
- Face recognition and clustering

 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

 License

MIT License

 Acknowledgments

- face_recognition library
- Google Cloud Platform
- Streamlit framework
