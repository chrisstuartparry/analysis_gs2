#!/bin/bash



# Pattern to match input files
pattern=aky_*.in

# Path to the GS2 executable
gs2_path="../../../gs2/bin/gs2"  # Adjust as necessary

# Loop over files and run GS2
for file in $pattern
do
    # Create a directory for the output files
    output_dir="${file%.in}"
    mkdir -p "${output_dir}"

    # Change to the output directory

    cp ${file} ${output_dir}/
    # Run GS2 simulation
    mpirun --np 16 $gs2_path ${output_dir}/${file} | tee "$output_dir/OUTPUT"


done

echo "All simulations completed."