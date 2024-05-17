from inpEditor import *
from extractFromINP import *
from utils import *
import os

# For single case:
# root_path = r"d:\CrackImage\PolyFEM\neper\16-betterGB"
# wp_name = "LocallyFinerMeshes"
# path = os.path.join(root_path, wp_name)
# old_inp_name = "poly_01_quad.inp"
# new_inp_name = "poly_01_quad_modified.inp"

# src = os.path.join(root_path, "LocallyFinerMeshes", old_inp_name)
# new = os.path.join(root_path, wp_name, new_inp_name)

# inpModifier(src, new, part_name="Notched")
# extractFromINP(path, new_inp_name)

# For multiple cases:
root_path = r"d:\lzl\LocallyFinerMeshes"

for wp_name in ["wp{:03d}".format(i) for i in range(1,11,1)]:
    path = os.path.join(root_path, wp_name)
    old_inp_name = "poly_quad.inp"
    new_inp_name = "poly_quad_modified.inp"

    src = os.path.join(root_path, wp_name, old_inp_name)
    new = os.path.join(root_path, wp_name, new_inp_name)

    inpModifier(src, new, part_name="Notched")
    extractFromINP(path, new_inp_name)