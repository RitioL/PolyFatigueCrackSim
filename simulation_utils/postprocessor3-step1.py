# Step 1: Extract selected frames' PHILSM information from Odb file
import json
import os
import sys
from extractFromODB import extractFromODB

wp_name = sys.argv[1]
frame = int(sys.argv[2])

# Load the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))

wp_path = os.path.join(root_path, wp_name)
extractFromODB(wp_path, "Job-2.odb", frame=frame)
