import psutil
import os
from pathlib import Path
from shared_constants import RESULTS_FOLDER

def show_system_stats():
    """Get system statistics for admin dashboard"""
    stats = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'clusters_count': len(list(Path(RESULTS_FOLDER).glob('cluster_*'))),
        'total_images': sum(
            len(list(Path(RESULTS_FOLDER).glob(f'cluster_*/*.{ext}')))
            for ext in ['jpg', 'jpeg', 'png']
        )
    }
    return stats