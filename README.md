# Data and code for visualizations related to the Nature Communications publication: Federated Learning Enables Big Data for Rare Cancer Boundary Detection.

Provided here are csv files for data as well as scripts for processing and visualization related to the work in the Nature Communications publication: Federated Learning Enables Big Data for Rare Cancer Boundary Detection.

## The folders in this top level directory are as follows:
- ***QualitativeExamples***: Nifti files showing MRI scans, ground truth segmentations, and both public initial and final consensus model segmentation outputs in order to provide examples where there were small, medium, and large improvements of final consensus over public initial model segmentations
- ***SourceData***: A folder containing a subfolder of scripts to produce plots and tables, as well as a zipped archive of all data csvs providing source data that the scripts will use
- ***fets_paper_figures***: Source code to create figures and manipulate pandas dataframes
- ***output***: The default location for script png file output, an alternate location can be provided when running the scripts if desired

## Steps for setup:
1. Create a python virtual environment(tested with Python 3.8) and install by running, 'pip install --upgrade pip' followed by, 'pip install .' from the top directory.
2. Run scripts using this virtual environment from within the scripts directory.

The scripts save images to disc and/or print latex code (for tables) to stdout.
