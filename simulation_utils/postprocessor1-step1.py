# Step 1: Extract the last frame's PHILSM information from Odb file
from extractFromODB import *
import os
import json

with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))

for wp_name in ["wp{:03d}".format(i) for i in range(1,101,1)]:
    wp_path = os.path.join(root_path, wp_name)
    job_name = "Job-2.odb"
    # Extracting the last frame, instead of all frames, is more efficient.
    if os.path.exists(wp_path):
        extractFromODB(wp_path, job_name, -1)