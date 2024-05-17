# Check individually
import os

signal = 1 # 0 first then 1
id = 3
frame = -20

wp_name = "wp0" + str(id)
root_path = r"d:\lzl\LocallyFinerMeshes"
wp_path = os.path.join(root_path, wp_name)
job_name = "Job-2.odb"
save_path = [root_path + str(i) for i in [r"\images-ebsd", r"\images-crack", r"\images-both"]]

if not signal:
    # Extract philsm information from odb file
    from extractFromODB import *
    
    extractFromODB(wp_path,job_name,frame)

else:
    # Draw EBSD and crack figures
    from utils import *
        
    path = os.path.join(root_path, wp_name)
    save_signal = drawCrack(path, save_path=save_path[1], save_name=wp_name)

    if save_signal:
        # drawEBSD(path, save_path=save_path[0], save_name=wp_name)

        input = [os.path.join(path, wp_name + ".png") for path in save_path]
        overlayImages(*input)