import os
import json
import numpy as np
from pathlib import Path

class EncodingsManager:
    def __init__(self, results_path):
        self.results_path = results_path
        self.encodings_file = os.path.join(results_path, 'encodings.json')
        self.encodings = self.load_encodings()
        
        # Create results directory if it doesn't exist
        os.makedirs(results_path, exist_ok=True)
    
    def load_encodings(self):
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'r') as f:
                    data = json.load(f)
                    return {k: [np.array(enc) for enc in v] for k, v in data.items()}
            return {}
        except Exception as e:
            print(f"Error loading encodings: {e}")
            return {}

    def save_encodings(self):
        try:
            serializable_encodings = {
                k: [enc.tolist() for enc in v] 
                for k, v in self.encodings.items()
            }
            with open(self.encodings_file, 'w') as f:
                json.dump(serializable_encodings, f)
            return True
        except Exception as e:
            print(f"Error saving encodings: {e}")
            return False

    def add_encoding(self, cluster_id, encoding):
        if cluster_id not in self.encodings:
            self.encodings[cluster_id] = []
        self.encodings[cluster_id].append(encoding)
        self.save_encodings()