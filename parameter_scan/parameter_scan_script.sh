#!/bin/bash



# Pattern to match input files
pattern=cyclone_like_alvaro_ky_100.in

# Path to the GS2 executable
gs2_path="../gs2/bin/gs2"  # Adjust as necessary

# Loop over files and run GS2
for file in $pattern
do
    # Create a directory for the output files
    output_dir="output_ky_${file##*_}"
    mkdir -p "${output_dir}"

    # Change to the output directory

    cp ${file} ${output_dir}/
    # Run GS2 simulation
    mpirun --np 2 $gs2_path ${output_dir}/${file} | tee "$output_dir/OUTPUT"

    # Wait for a while to ensure all files are generated

done

echo "All simulations completed."

