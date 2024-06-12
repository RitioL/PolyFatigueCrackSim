import subprocess

# Execute step 1
# Extract selected frames' PHILSM information from Odb file
subprocess.run(["python", "simulation_utils\postprocessor2-step1.py"])

# Execute step 2
# Draw EBSD and crack images
subprocess.run(["python", "simulation_utils\postprocessor2-step2.py"])
