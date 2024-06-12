# Step 2: Draw EBSD and crack images
import json
import os
import sys
from utils import drawCrack, drawEBSD, overlayImages

wp_name = sys.argv[1]
frame = int(sys.argv[2])

# Load the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))
save_path = [root_path + str(i) for i in [r"\images-ebsd", r"\images-crack", r"\images-both"]]

wp_path = os.path.join(root_path, wp_name)

# Draw EBSD and crack path images
drawCrack(wp_path, 'philsm.csv', frame, save_path=save_path[1], save_name=wp_name)
drawEBSD(wp_path, save_path=save_path[0], save_name=wp_name)
input_files = [os.path.join(path, wp_name + ".png") for path in save_path]
overlayImages(*input_files)
