# Step 2: Draw EBSD and crack images
import os
import json
from utils import *

# Load the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))

# Check if the save paths exist
save_path = [root_path + str(i) for i in [r"\images-ebsd", r"\images-crack", r"\images-both"]]
for path in save_path:
    if not os.path.exists(path):
        os.makedirs(path)

# List of all valid workplace folders
valid_wps = [f for f in os.listdir(root_path) if f.startswith('wp')]

# Choose the turning point frame to visualize EBSD and crack
for wp_name in sorted(valid_wps):
    wp_path = os.path.join(root_path, wp_name)
    print(f"{wp_name}:")
    stop_frame, _, _, _ = analyzeCrack(wp_path)

    # Draw EBSD and crack path images
    drawCrack(wp_path, 'philsm_selected_frames.csv', stop_frame, save_path=save_path[1], save_name=wp_name)
    drawEBSD(wp_path, save_path=save_path[0], save_name=wp_name)
    input = [os.path.join(path, wp_name + ".png") for path in save_path]
    overlayImages(*input)