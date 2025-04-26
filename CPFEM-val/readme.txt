This folder contains the necessary files for CPFEM validation, including input files, experimental and simulation results. The experimental data were obtained from uniaxial tensile tests on Inconel 718 specimens. The simulated stress-strain curve was derived from uniaxial tensile testing of a rectangular RVE, converted from reaction force and displacement data.

Building upon the work in [1], this study primarily adjusted the following parameters to achieve better agreement between the simulated and experimental curves:

Power law exponent: 100 → 12

Reference strain rate: 1e-03 → 1e-02

Critical resolved shear stress: 315 → 285

A brief overview of the folder structure is provided below:

1. Subfolder: "comparison"
	· CPFEM_validation.opju
		· Comparison of simulation and experimental data, stored as an Origin file.
	· CPFEM_validation.png
		· Comparison of simulation and experimental data, stored as an PNG figure.

2. Subfolder: "stress-strain_curve"
	· stress-strain_12_1e-02_200-650-285.xlsx
		· Excel file containing the simulated stress-strain curve data.

3. Subfolder: "workplace"
	· command_GUI.bat
		· Launches the Abaqus GUI. Double-click to run.
	· command_start.bat
		· Starts the simulation. Double-click to execute.
	· Job-1.odb
		· Abaqus simulation results.
	· Job-1-copy.inp
		· Input file for Abaqus.

4. File: "subroutines_revised.for"
	UMAT subroutine for Abaqus.

Reference:
[1] Yuan, G. J., Zhang, X. C., Chen, B., Tu, S. T., & Zhang, C. C. (2020). Low-cycle fatigue life prediction of a polycrystalline nickel-base superalloy using crystal plasticity modelling approach. Journal of Materials Science & Technology, 38, 28-38.