# Extract PHILSM information from Odb file
from extractFromODB import *
import os
import json

frame = -1

with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))

for wp_name in ["wp{:03d}".format(i) for i in range(1,2,1)]:
    wp_path = os.path.join(root_path, wp_name)
    job_name = "Job-2.odb"
    extractFromODB(wp_path,job_name,frame)