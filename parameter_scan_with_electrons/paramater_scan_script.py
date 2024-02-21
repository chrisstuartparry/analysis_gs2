# import glob
import os
import shutil
import subprocess

# Pattern to match input files
# pattern = "cyclone_like_alvaro_ky_125.in"
files = [
    "cyclone_like_alvaro_ky_175.in",
    "cyclone_like_alvaro_ky_600.in",
    "cyclone_like_alvaro_ky_700.in",
    "cyclone_like_alvaro_ky_800.in",
    "cyclone_like_alvaro_ky_900.in",
]
# Path to the GS2 executable
gs2_path = "../../gs2/bin/gs2"  # Adjust as necessary

# Find files matching the pattern
# files = glob.glob(pattern)

for file in files:
    # Create a directory for the output files
    output_dir = f"output_ky_{file.split('_')[-1]}"
    os.makedirs(output_dir, exist_ok=True)

    # Copy file to the output directory
    shutil.copy(file, os.path.join(output_dir, file))

    # Run GS2 simulation
    command = f"mpirun --np 16 {gs2_path} {os.path.join(output_dir, file)}"
    with open(f"{output_dir}/OUTPUT", "w") as output_file:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        for line in process.stdout:
            output_file.write(line.decode())

    # Optional: Wait for a while to ensure all files are generated
    # time.sleep(delay_in_seconds) # Uncomment and set delay_in_seconds as needed

print("All simulations completed.")
