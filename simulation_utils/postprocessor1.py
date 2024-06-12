import subprocess

# Execute step 1
# Extract the last frame's PHILSM information from Odb file
subprocess.run(["python", "simulation_utils\postprocessor1-step1.py"])

# Execute step 2
# Analyze whether the crack length meets the standard and delete folders that do not meet the standard
subprocess.run(["python", "simulation_utils\postprocessor1-step2.py"])
