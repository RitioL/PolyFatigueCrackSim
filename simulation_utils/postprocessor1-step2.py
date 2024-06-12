# Step 2: Analyze whether the crack length meets the standard and delete folders that do not meet the standard
import os
import json
import shutil
from utils import *

with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))
save_path = [root_path + str(i) for i in [r"\images-ebsd", r"\images-crack", r"\images-both"]]
    
# Check if the save path exists
for path in save_path:
    if not os.path.exists(path):
        os.makedirs(path)

# Delete folders that do not meet the standard
for wp_name in ["wp{:03d}".format(i) for i in range(1,101,1)]:
    wp_folder_path = os.path.join(root_path, wp_name)
    if os.path.exists(wp_folder_path):
        if not isInvalidCrack(wp_folder_path):
            if os.path.isdir(wp_folder_path):
                shutil.rmtree(wp_folder_path)
                print(f"    Deleted {wp_folder_path}")
        else:
            print(f"    Remained {wp_folder_path}")
    
