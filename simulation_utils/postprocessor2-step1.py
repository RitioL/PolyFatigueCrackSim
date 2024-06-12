# Step 1: Extract selected frames' PHILSM information from Odb file
import json
import os
from extractFromODB import *

# Load the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))

# List of all valid workplace folders
valid_wps = [f for f in os.listdir(root_path) if f.startswith('wp')]

# Extract selected frames' philsm information from odb file
for wp_path in [os.path.join(root_path, wp) for wp in valid_wps]:
    extractFramesFromODB(wp_path, "Job-2.odb", auto=True)