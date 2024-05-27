from inpEditor import *
from extractFromINP import *
import os

# For single case:
# root_path = r"d:\CrackImage\PolyFEM\neper\16-betterGB"
    
# wp_name = "LocallyFinerMeshes"
# path = os.path.join(root_path, wp_name)
# job_name = "Job-1.inp"
# new_job_name = "Job-1_modified.inp"
# src = os.path.join(path, job_name)
# new = os.path.join(path, new_job_name)

# print(f"{wp_name}:")
# cl = getAverageElementLengthWithinGrain(path)

# modifyDamage(src, new, cl=cl, properties=[1e-9])
# modifyStep(new, new, step_time=50)
# modifyAmplitude(new, new, addAmplitude(0.1,1.0,5,30,print=False))

# For multiple cases:
root_path = r"d:\lzl\LocallyFinerMeshes"

for wp_name in ["wp{:03d}".format(i) for i in range(1,11,1)]:        
    path = os.path.join(root_path, wp_name)
    job_name = "Job-1.inp"
    new_job_name = "Job-1_modified.inp"
    src = os.path.join(path, job_name)
    new = os.path.join(path, new_job_name)

    print(f"{wp_name}:")
    cl = getAverageElementLengthWithinGrain(path)

    modifyDamage(src, new, cl=cl, properties=[1e-11])
    modifyStep(new, new, step_time=500)
    modifyAmplitude(new, new, addAmplitude(0.1,1.0,5,100,print=False))