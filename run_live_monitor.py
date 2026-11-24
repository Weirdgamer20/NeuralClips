import os
import sys

# Ensure project root is on sys.path regardless of where this script is called from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.env_loader import load_env
load_env()

from jobs.realtime_stream_monitor import RealTimeStreamMonitor

if __name__ == "__main__":
    print("==================================================================")
    print("NEURALCLIPS REAL-TIME GTA 6 LIVESTREAM MONITOR & AUTO-UPLOADER")
    print("==================================================================")
    print("Working Directory:", BASE_DIR)
    print("Starting continuous live capture loop...")
    monitor = RealTimeStreamMonitor()
    monitor.run_continuous(interval_seconds=60, limit=5, chunk_seconds=30)
