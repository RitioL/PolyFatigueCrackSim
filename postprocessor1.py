# Extract PHILSM information from Odb file
from extractFromODB import *
import os

frame = -1
root_path = r"d:\lzl\LocallyFinerMeshes"

for id in range(1,6,1):
    wp_name = "wp0" + str(id)
    wp_path = os.path.join(root_path, wp_name)
    job_name = "Job-2.odb"
    extractFromODB(wp_path,job_name,frame)