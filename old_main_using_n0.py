import glob
import os
import re

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd
from netCDF4 import Dataset  # noqa: E402

# directory_two_up = Path(__file__).resolve().parents[1]


def generate_fig_and_axs(num_plots: int) -> tuple:
    """
    Generates a figure and axes for the number of plots specified, with a maximum of 3 columns
    num_plots: int = number of plots to be generated
    """
    ncols = min(num_plots, 3)
    nrows = (num_plots + ncols - 1) // ncols if num_plots > 3 else 1
    fig, axs = plt.subplots(
        nrows, ncols, figsize=(15, 5 * nrows), constrained_layout=True, squeeze=False
    )
    return fig, axs


def extract_variables(file_path: str, over_all_t: bool = False) -> tuple:
    """Extracts certain variables from netCDF formatted file at file_path.
    Variables extracted are omega (itself extracted into frequency and growth rate), t, ky, and drhodpsi.


    Args:
        file_path (str): _description_
        over_all_t (bool, optional): If over_all_t is True, the entire omega array (and t itself) is returned, otherwise the final frequency, growth rate, and ky are returned.  Defaults to False.

    Returns:
        (tuple): A tuple containing the desired variables. If over_all_t is True, the tuple contains t, frequency_over_all_t, and growth_rate_over_all_t. Otherwise, the tuple contains final_frequency, final_growth_rate, and ky.
    """
    data = Dataset(
        file_path,
        "r",
    )
    omega = data.variables["omega"][:]  # Extracts the entire 'omega' array
    print("omega:\n", data.variables["omega"])
    t = data.variables["t"][:]  # Extracts the entire 't' array
    frequency_over_all_t = omega[
        :, 0, 0, 0
    ]  # Extracts the first component of omega for all t
    growth_rate_over_all_t = omega[
        :, 0, 0, 1
    ]  # Extracts the second component of omega for all t

    ky_raw = data.variables["ky"]
    ky = ky_raw[0]
    print("ky:\n", ky)
    drhodpsi_raw = data.variables["drhodpsi"]
    drhodpsi = drhodpsi_raw[0]
    print("drhodpsi_raw:\n", drhodpsi_raw)
    print("drhodpsi:\n", drhodpsi)
    beta_raw = data.variables["beta"]
    beta = beta_raw[0]
    print("beta_raw:\n", beta_raw)
    print("beta:\n", beta)

    final_frequency = omega[-1, 0, 0, 0]
    final_growth_rate = omega[-1, 0, 0, 1]
    data.close()

    if over_all_t:
        return t, frequency_over_all_t, growth_rate_over_all_t
    else:
        return final_frequency, final_growth_rate, ky


def plot_data_for_all_t(axs, row, col, t, frequency_over_all_t, growth_rate_over_all_t):
    axs[row, col].plot(t, frequency_over_all_t, label="Frequency")
    axs[row, col].plot(t, growth_rate_over_all_t, label="Growth Rate")
    axs[row, col].set_xlabel("Time")
    axs[row, col].set_ylabel("Frequency & Growth Rate")
    axs[row, col].set_title(f"File: {os.path.basename(file_path)}")
    axs[row, col].legend()


def extract_n0(directory: str) -> int:
    match = re.search(r"output_ky_(\d+).in", directory)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Could not extract n0 value from {directory}")


def get_raw_directories_without_n0(relative_file_path: str) -> list[str]:
    return glob.glob(relative_file_path)


relative_file_path: str = "exploratory_beta_scan/output_ky_*.in"
unsorted_directories_with_n0 = [
    (extract_n0(directory), directory)
    for directory in get_raw_directories_without_n0(relative_file_path)
]
sorted_directories_with_n0 = sorted(
    unsorted_directories_with_n0, key=lambda directory_with_n0: directory_with_n0[0]
)


directories = [directory[1] for directory in sorted_directories_with_n0]
n0_values = [directory[0] for directory in sorted_directories_with_n0]


num_plots = len(sorted_directories_with_n0)
fig, axs = generate_fig_and_axs(num_plots)

# for index, directory_with_n0 in enumerate(sorted_directories_with_n0):

number_of_directories = len(sorted_directories_with_n0)
final_values_for_each_ky = np.empty((number_of_directories, 4))

for index, directory_tuple in enumerate(sorted_directories_with_n0):
    n0_value, directory_string = directory_tuple
    file_path = f"{directory_string}/cyclone_like_alvaro_ky_{n0_value}.out.nc"
    if os.path.exists(file_path):
        row, col = divmod(index, 3)
        t, frequency_over_all_t, growth_rate_over_all_t = extract_variables(
            file_path, over_all_t=True
        )
        plot_data_for_all_t(
            axs, row, col, t, frequency_over_all_t, growth_rate_over_all_t
        )
        final_frequency, final_growth_rate, ky = extract_variables(file_path)
        print("n0: ", n0_value)
        final_values_for_each_ky[index] = [
            final_frequency,
            final_growth_rate,
            ky,
            n0_value,
        ]
        print(
            "Final Values List: ",
            [final_frequency, final_growth_rate, ky, n0_value],
        )
    else:
        print(f"File {file_path} not found.")
print("Final values for each ky: \n", final_values_for_each_ky)
final_values_for_each_ky_df = pd.DataFrame(
    final_values_for_each_ky, columns=["Frequency", "Growth Rate", "ky", "n0"]
)
# final_values_for_each_ky_df.set_index("n0", inplace=True)
print("Final values for each ky as a dataframe: \n", final_values_for_each_ky_df)
fig.suptitle("Frequency and Growth Rate vs Time")
plt.show()

# Plot the final values for each ky
# def plot_final_values_for_each_ky(final_values_for_each_ky_df: DataFrame) -> None:
final_values_for_each_ky_df.set_index("ky", inplace=True)
final_values_for_each_ky_df.drop("n0", axis=1, inplace=True)
final_values_for_each_ky_df.plot()
plt.show()
