import os

import f90nml
import numpy as np


def generate_input_files(input_file_path, param_group, param_name, values, output_dir):
    # Read the original input file
    nml = f90nml.read(input_file_path)

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over the provided values to modify the parameter and generate new files
    for i, value in enumerate(values):
        # Modify the specified parameter
        nml[param_group][param_name] = value

        # Generate a new filename based on the parameter value
        new_filename = f"{param_name}_{value}.in"
        new_file_path = os.path.join(output_dir, new_filename)

        # Write out the new input file
        nml.write(new_file_path, force=True)

    print(
        f"Generated {len(values)} input files with variations of {param_name} in '{output_dir}' directory."
    )


# Example usage
input_file_path = "./parameter_scans/input_with_comments.in"
param_group = "kt_grids_single_parameters"
param_name = "aky"
values = np.arange(5, 155, 5) / 100
output_dir = "./parameter_scans/beta_ky_scan/"

# Generate the input files
generate_input_files(input_file_path, param_group, param_name, values, output_dir)
