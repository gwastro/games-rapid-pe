# Example of analyzing a simualted BNS signal with the GAMES sampler

To make sure you have the software set up, make sure to install the
needed python packages from requirements.txt

# The run.sh script breaks this down into a few tasks

# 1) downloading the precalculated mapping file 
# 2) creating the injection file (see e.g injection.ini)
# 3) running pycbc inference, this will interally create simulated data 
     with the provided injection file and set up a number of steps needed
     for parameter marginalization. It will then use the sampler and 
     save a file with samples with the associated (non-marginalized) paramters
# 4) Runs a separate script to reconstruct any marginalized parameters
# 5) Plots the resulting samples
