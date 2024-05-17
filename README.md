# PolycrystalFatigueCrackSim

This repository contains scripts for the batch generation of polycrystalline RVE models and finite element analysis operations. These scripts are used to simulate the generation of fatigue cracks in polycrystalline materials. The involved software includes Neper, Gmsh, and Abaqus 2022.

## Specific Operation Process

### Preprocessing:
1. **Run `scriptGenerator.py`**
    - **Note:** This script generates the batch polycrystal model generation script `neper.sh` and the Abaqus operation startup script `startup.bat`.
2. **Change the directory to where `neper.sh` is located in the Ubuntu command line, then enter the following command:**
    ```bash
    ./neper.sh
    ```
    - **Note:** Different systems have different line break characters, which may cause script execution errors. `scriptGenerator.py` has resolved this issue. If needed, you can convert it in the Ubuntu command line with:
    ```bash
    sed -i 's/\r$//' neper.sh
    ```
3. **Run `editInp1.py`**
    - **Note:** This script adds material information to the `inp` file.
4. **Run `preprocessor.py`**
    - **Note:** This script sets various simulation parameters such as analysis steps and boundary conditions.
5. **Run `editInp2.py`**
    - **Note:** This script batch modifies certain parameters.

### Execution:
6. **Run `startup.bat`**
    - **Note:** This script batch submits the jobs to Abaqus.

### Post-processing:
7. **Run `postprocessor1.py`**
    - **Note:** This script extracts the `philsm` values at nodes for crack plotting.
8. **Run `postprocessor2.py`**
    - **Note:** This script plots and saves EBSD and Crack diagrams.
9. **Run `postprocessor3.py`**
    - **Note:** This script filters and extracts results from different frames one by one.

## UMAT Instructions:
- `subroutines.for` is the original subroutine.
- `subroutines2.for` adds a non-local method to the original version.
- `subroutines3.for` adds an early-stopping mechanism to the original version.
