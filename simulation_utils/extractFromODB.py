# Extract element and node information from odb file
import odbAccess
from odbAccess import *
import csv
import os

def extractFromODB(path, job_name, frame=-1):
    odb_path = os.path.join(path,job_name)

    try:
        odb = openOdb(path=odb_path, readOnly=True)
    except OdbError:
        temp_path = "D:/CrackImage/trash/Job-2-9-es.odb"
        odbAccess.upgradeOdb(odb_path, temp_path)
        print("Odb file is from old version and has been updated.")
        odb = openOdb(path=temp_path, readOnly=True)
    
    instance = odb.rootAssembly.instances['NOTCHED-1']

    lastFrame = odb.steps['Step-1'].frames[frame]
    philsm = lastFrame.fieldOutputs['PHILSM']

    # Get node labels, corresponding coordinates and targeted values
    with open(os.path.join(path,'philsm.csv'), 'w') as csvfile:
        fieldnames = ['Node Label', 'X', 'Y', 'PHILSM']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()    
        for node, value in zip(instance.nodes, philsm.getScalarField().values):
            writer.writerow({'Node Label': node.label,
                            'X': node.coordinates[0],
                            'Y': node.coordinates[1],
                            'PHILSM': value.data
                            })

    odb.close()
    