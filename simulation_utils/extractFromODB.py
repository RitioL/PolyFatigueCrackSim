# Extract element and node information from odb file
import odbAccess
from odbAccess import *
import csv
import os

def extractFromODB(path, job_name, frame=-1):
    '''Extract philsm info from 1 selected frame of ODB file'''
    odb_path = os.path.join(path,job_name)

    try:
        odb = openOdb(path=odb_path, readOnly=True)
    except OdbError:
        # Version problem
        temp_path = "D:/temp/Job-2_temp.odb"
        odbAccess.upgradeOdb(odb_path, temp_path)
        print("Odb file is from old version and has been updated.")
        odb = openOdb(path=temp_path, readOnly=True)
    
    instance = odb.rootAssembly.instances['NOTCHED-1']
    step = odb.steps['Step-1']
    frame_idx = list(range(0, len(step.frames), 1))[frame]
    philsm = step.frames[frame].fieldOutputs['PHILSM']

    # Get node labels, corresponding coordinates and targeted values
    with open(os.path.join(path,'philsm.csv'), 'w') as csvfile:
        fieldnames = ['Frame', 'Node Label', 'X', 'Y', 'PHILSM']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()    
        for node, value in zip(instance.nodes, philsm.getScalarField().values):
            writer.writerow({'Frame': frame_idx,
                            'Node Label': node.label,
                            'X': node.coordinates[0],
                            'Y': node.coordinates[1],
                            'PHILSM': value.data
                            })

    odb.close()

def extractFramesFromODB(path, job_name, num_frames_to_extract=10, jump=2, auto=False):
    '''Extract philsm info from >1 selected frames of ODB file'''
    odb_path = os.path.join(path, job_name)

    try:
        odb = openOdb(path=odb_path, readOnly=True)
    except OdbError:
        # Version problem
        temp_path = "D:/temp/Job-2_temp.odb"
        odbAccess.upgradeOdb(odb_path, temp_path)
        print("Odb file is from old version and has been updated.")
        odb = openOdb(path=temp_path, readOnly=True)

    instance = odb.rootAssembly.instances['NOTCHED-1']
    step = odb.steps['Step-1']
    num_frames = len(step.frames)

    # Adjust "num_frames_to_extract" and "jump" automatically
    if auto:
        if num_frames >= 40:
            jump = 2
            num_frames_to_extract = 20
        else:
            jump = 2
            num_frames_to_extract = 15

    frames_to_extract = set()  # Using set to avoid duplicates

    # Ensure the last 5 frames are included, if there are at least 5 frames
    if num_frames >= 5:
        last_five_frames = list(range(num_frames - 5, num_frames))
    else:
        last_five_frames = list(range(num_frames))

    frames_to_extract.update(last_five_frames)

    # Adjust the number of frames to extract to account for the last 5 frames
    remaining_frames_to_extract = num_frames_to_extract - len(last_five_frames)

    # If there are enough frames for jumping extraction
    if num_frames >= (remaining_frames_to_extract * jump) + len(last_five_frames):
        extra_frames = list(range(num_frames - len(last_five_frames) - 1 - jump, 
                                num_frames - len(last_five_frames) - 1 - remaining_frames_to_extract * jump, 
                                -jump))
        frames_to_extract.update(extra_frames)
    # If there are enough frames but not for jumping extraction
    elif num_frames >= remaining_frames_to_extract:
        extra_frames = list(range(num_frames - len(last_five_frames) - 1, 
                                num_frames - len(last_five_frames) - 1 - remaining_frames_to_extract, 
                                -1))
        frames_to_extract.update(extra_frames)
    # If there are not enough frames, extract all available frames
    else:
        extra_frames = list(range(num_frames - len(last_five_frames) - 1, -1, -1))
        frames_to_extract.update(extra_frames)

    # Convert set to sorted list
    frames_to_extract = sorted(frames_to_extract)
    
    output_csv = os.path.join(path, 'philsm_selected_frames.csv')
    
    with open(output_csv, mode='w') as csvfile:
        fieldnames = ['Frame', 'Node Label', 'X', 'Y', 'PHILSM']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for frame_idx in frames_to_extract:
            frame = step.frames[frame_idx]
            philsm = frame.fieldOutputs['PHILSM']
            
            for node, value in zip(instance.nodes, philsm.getScalarField().values):
                writer.writerow({'Frame': frame_idx,
                                'Node Label': node.label,
                                'X': node.coordinates[0],
                                'Y': node.coordinates[1],
                                'PHILSM': value.data
                                })

    odb.close()