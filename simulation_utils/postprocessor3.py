import subprocess

# Values to be passed to the scripts
wp_name = "wp038"
frame = 19

# Execute step 1
# Extract selected frames' PHILSM information from Odb file
subprocess.run(["python", "simulation_utils\postprocessor3-step1.py", wp_name, str(frame)])

# Execute step 2
# Draw EBSD and crack images
subprocess.run(["python", "simulation_utils\postprocessor3-step2.py", wp_name, str(frame)])
