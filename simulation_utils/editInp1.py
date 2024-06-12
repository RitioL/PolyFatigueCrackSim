from inpEditor import *
from extractFromINP import *
from utils import *
import os
import json

with open('config.json', 'r') as f:
    config = json.load(f)
root_path = config.get('root_path')
ori_seed = config.get('ori_seed')

# For multiple cases:
for wp_name in ["wp{:03d}".format(i) for i in range(1,101,1)]:
    path = os.path.join(root_path, wp_name)
    old_inp_name = "poly_quad.inp"
    new_inp_name = "poly_quad_modified.inp"

    src = os.path.join(root_path, wp_name, old_inp_name)
    new = os.path.join(root_path, wp_name, new_inp_name)

    inpModifier(src, new, part_name="Notched", ori_seed=ori_seed)
    extractFromINP(path, new_inp_name)