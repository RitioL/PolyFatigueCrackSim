import os
import json

with open('config.json', 'r') as f:
    config = json.load(f)
root_path = config.get('root_path')
smooth_grain_boundary = config.get('smooth_grain_boundary')
os.chdir(root_path)

script1_content = [] # Script for gmsh
script2_content = [] # Script for generating polycrystalline model
script3_content = [] # Script for FEM calculation

# 1. Script for gmsh: Smooth Grain Boundary
if smooth_grain_boundary:
    script1_content.append(
            "Merge \"poly_msh.msh4\";\n"
            "Mesh.RecombinationAlgorithm = 1;\n"
            "RecombineMesh;\n"
            "Mesh.SecondOrderLinear = 1;\n"
            "Mesh.SubdivisionAlgorithm = 1;\n"
            "Mesh.SaveGroupsOfElements = 0;\n"
            "RefineMesh;"
        )

# 1. Script for gmsh: Non-smooth Grain Boundary
else:
    script1_content.append(
            "Merge \"poly_msh.msh\";\n"
            "Mesh.SaveGroupsOfElements = 0;\n"
        )

for id in range(1, 2, 1):
    # make directories for abaqus workplace
    wp_name = "wp"+f"{id:03d}"
    os.makedirs(wp_name, exist_ok=True)

    # make gmsh scripts for each abaqus workplace
    with open(os.path.join(wp_name, "poly_quad.geo"), 'w', newline='\r\n') as newFile:
        newFile.writelines(script1_content)

    # 2. Make neper scripts: Smooth Grain Boundary
    if smooth_grain_boundary:
        script2_content.append(
            f"cd {wp_name}\n"
            "neper -T -n from_morpho -dim 2 -domain \"square(1.5,1.0)\" "
            "-morpho \"diameq:lognormal(0.07923,0.02839),1-sphericity:lognormal(0.14,0.07)\" "
            f"-id {id} -reg 1 -o poly.tess\n"
            "neper -M poly.tess -nset edges -cledge \"(y>0.25&&y<0.75&&x>-0.01&&x<1.0)?0.08:0.08\" -order 1 -format msh4 -o poly_msh\n"
            "gmsh poly_quad.geo -2 -format inp\n"
            "cd ..\n"
            )

    # 2. Make neper scripts: Non-smooth Grain Boundary
    else:
        script2_content.append(
            f"cd {wp_name}\n"
            "neper -T -n from_morpho -dim 2 -domain \"square(1.5,1.0)\" "
            "-morpho \"diameq:lognormal(0.07923,0.02839),1-sphericity:lognormal(0.14,0.07)\" "
            f"-id {id} -reg 1 -o poly.tess\n"
            "neper -M poly.tess -elttype quad -cl 1/101 -order 1 -format msh -o poly_msh\n"
            "gmsh poly_quad.geo -2 -format inp\n"
            "cd ..\n"
            )

    # 3. Make abaqus scripts
    script3_content.append(
        f"cd {wp_name}\n"
        "if exist \"Job-2.lck\" del \"Job-2.lck\"\n"
        "cmd/c abq2022 cpus=8 job=Job-2 user=..\\subroutines3_revised.for input=Job-1_modified.inp int ask=OFF\n"
        "if exist \"Job-2.dat\" del \"Job-2.dat\"\n"
        "if exist \"Job-2.stt\" del \"Job-2.stt\"\n"
        "cd ..\n"
        )
    
    
script3_content.append("pause\n")

with open('neper.sh', 'w', newline='\n') as newFile:
    newFile.writelines(script2_content)

with open('startup.bat', 'w', newline='\r\n') as newFile:
    newFile.writelines(script3_content)


