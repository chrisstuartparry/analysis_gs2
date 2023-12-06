import glob
import os
import re
from typing import Union

import matplotlib

matplotlib.use("GTK3Agg")


import matplotlib.pyplot as plt  # noqa: E402
from netCDF4 import Dataset  # noqa: E402

# directory_two_up = Path(__file__).resolve().parents[1]


def generate_fig_and_axs(num_plots: int) -> tuple:
    ncols = min(num_plots, 4)
    nrows = (num_plots + ncols - 1) // ncols if num_plots > 4 else 1
    fig, axs = plt.subplots(
        nrows, ncols, figsize=(15, 5 * nrows), constrained_layout=True, squeeze=False
    )
    return fig, axs


def extract_n0(directory: str) -> Union[str, None]:
    match = re.search(r"output_ky_(\d+).in", directory)
    if match:
        return int(match.group(1))
    else:
        return None


def process_data(file_path: str) -> None:
    data = Dataset(
        file_path,
        "r",
    )
    omega = data.variables["omega"][:]  # Extracts the entire 'omega' array
    t = data.variables["t"][:]  # Extracts the entire 't' array
    frequency_over_all_t = omega[
        :, 0, 0, 0
    ]  # Extracts the first component of omega for all t
    growth_rate_over_all_t = omega[
        :, 0, 0, 1
    ]  # Extracts the second component of omega for all t
    data.close()

    plt.plot(t, frequency_over_all_t, label="Frequency")
    plt.plot(t, growth_rate_over_all_t, label="Growth Rate")
    plt.xlabel("Time")
    plt.ylabel("Frequency & Growth Rate")
    plt.title(f"Frequency & Growth Rate vs Time for {file_path}")
    plt.legend()
    plt.show()


directories_unsorted: list = glob.glob("parameter_scan/output_ky_*.in")
directory_unsorted_tuples = [
    (extract_n0(directory), directory)
    for directory in directories_unsorted
    if (extract_n0(directory) is not None)
]
# print("directory_unsorted_tuple:", directory_unsorted_tuples)

# extracted_values = [
#     (extract_n0(directory), directory) for directory in directories_unsorted
# ]


# directory_unsorted_tuples = [
#     (n0, directory) for n0, directory in extracted_values if n0 is not None
# ]

directories_sorted = sorted(directory_unsorted_tuples, key=lambda x: int(x[0]))
directories = [directory[1] for directory in directories_sorted]
n0_values = [directory[0] for directory in directories_sorted]
# print("directories:", directories_sorted)

for directory_tuple in directories_sorted:
    n0_value, directory_string = directory_tuple
    if n0_value:
        file_path = f"{directory_string}/cyclone_like_alvaro_ky_{n0_value}.out.nc"
        if os.path.exists(file_path):
            process_data(file_path)
        else:
            print(f"File {file_path} not found.")
    else:
        print(f"Could not extract n0 value from {directory_string}")
