import os
from pathlib import Path

# Get base directory
BASE_DIR = Path(__file__).parent.absolute()

# Define paths
DATASET_FOLDER = os.path.join(BASE_DIR, 'dataset')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
ENCODINGS_FILE = os.path.join(RESULTS_FOLDER, 'encodings.json')

# Create necessary directories
os.makedirs(DATASET_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
