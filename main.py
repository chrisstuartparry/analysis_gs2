import glob
import os
from typing import Any

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from netCDF4 import Dataset, Variable  # noqa: E402
from numpy import ndarray
from numpy.ma import MaskedArray
from numpy.typing import NDArray

VariableSubset = NDArray | MaskedArray | Any


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


def extract_variables(
    file_path: str, extra_variables: list, over_all_t: bool = False
) -> tuple[Any, Any, Any] | tuple[Any, Any, dict[str, Any]]:
    """Extracts certain variables from netCDF formatted file at file_path.
    Variables extracted are omega (itself extracted into frequency and growth rate), t, ky, and drhodpsi.


    Args:
        file_path (str): _description_
        over_all_t (bool, optional): If over_all_t is True, the entire omega array (and t itself) is returned, otherwise the final frequency, growth rate, and ky are returned.  Defaults to False.

    Returns:
        (tuple): A tuple containing the desired variables. If over_all_t is True, the tuple contains t, frequency_over_all_t, and growth_rate_over_all_t. Otherwise, the tuple contains final_frequency, final_growth_rate, and ky.
    """
    data: Dataset = Dataset(
        file_path,
        "r",
    )
    omega: VariableSubset = data.variables["omega"][
        :
    ]  # Extracts the entire 'omega' array
    print("omega:\n", data.variables["omega"])
    t: VariableSubset = data.variables["t"][:]  # Extracts the entire 't' array
    frequency_over_all_t = omega[
        :, 0, 0, 0
    ]  # Extracts the first component of omega for all t
    growth_rate_over_all_t = omega[
        :, 0, 0, 1
    ]  # Extracts the second component of omega for all t
    extra_variables_values: dict = {}
    for variable in extra_variables:
        variable_raw: Variable = data.variables[variable]
        variable_value: VariableSubset = variable_raw[0]
        print(f"{variable}_raw = ", variable_raw)
        print(f"{variable_value} = ", variable)
        extra_variables_values[variable] = variable_value
    print("extra_variables_values:\n", extra_variables_values)

    final_frequency = omega[-1, 0, 0, 0]
    final_growth_rate = omega[-1, 0, 0, 1]
    data.close()

    if over_all_t:
        return t, frequency_over_all_t, growth_rate_over_all_t
    else:
        return (final_frequency, final_growth_rate, extra_variables_values)


def plot_data_for_all_t(
    axs: ndarray,
    row: int,
    col: int,
    t: VariableSubset,
    frequency_over_all_t,
    growth_rate_over_all_t,
    file_path: str,
):
    axs[row, col].plot(t, frequency_over_all_t, label="Frequency")
    axs[row, col].plot(t, growth_rate_over_all_t, label="Growth Rate")
    axs[row, col].set_xlabel("Time")
    axs[row, col].set_ylabel("Frequency & Growth Rate")
    axs[row, col].set_title(f"File: {os.path.basename(file_path)}")
    axs[row, col].legend()


def get_directories(directory_pattern: str) -> list[str]:
    """
    Returns a list of directories matching the pattern directory_pattern
    """
    all_files = glob.glob(directory_pattern)
    directories_only = [
        all_files[i] for i in range(len(all_files)) if os.path.isdir(all_files[i])
    ]
    return directories_only


def get_fig_axs_for_each_ky(relative_file_path: str, directories: list[str]) -> tuple:
    """
    Plots the final frequency and growth rate for each ky value in the directory pattern relative_file_path
    """

    num_directories: int = len(directories)
    num_plots: int = num_directories
    fig, axs = generate_fig_and_axs(num_plots)
    return fig, axs


def main() -> None:
    relative_file_path: str = "parameter_scans/beta_ky_scan/aky*"
    directories: list[str] = get_directories(relative_file_path)
    print("Directories: ", directories)
    file_names: list[str] = [
        directory.replace("parameter_scans/beta_ky_scan/", "")
        for directory in directories
    ]
    file_names = [file_name.replace(".in", "") for file_name in file_names]
    fig, axs = get_fig_axs_for_each_ky(relative_file_path, directories)

    number_of_directories = len(directories)
    final_values = np.empty((number_of_directories, 4))

    for index, directory in enumerate(directories):
        file_path = f"{directory}/{file_names[index]}.out.nc"
        if os.path.isfile(file_path):
            row, col = divmod(index, 3)
            t, frequency_over_all_t, growth_rate_over_all_t = extract_variables(
                file_path, ["ky", "beta"], over_all_t=True
            )
            plot_data_for_all_t(
                axs,
                row,
                col,
                t,
                frequency_over_all_t,
                growth_rate_over_all_t,
                file_path,
            )
            final_frequency, final_growth_rate, extra_variables_values = (
                extract_variables(file_path, ["ky", "beta"])
            )
            final_values[index] = [
                final_frequency,
                final_growth_rate,
                *extra_variables_values.values(),
            ]
            print(
                f"Final frequency and growth rate for {file_path} are {final_frequency} and {final_growth_rate} respectively"
            )
            print(f"Extra variables for {file_path} are {extra_variables_values}")
        else:
            print(f"File {file_path} not found.")
    print("Final values list: ", final_values)
    plt.suptitle("Frequency and Growth Rate vs Time")
    plt.show()

    final_values_df = pd.DataFrame(
        final_values, columns=["Final Frequency", "Final Growth Rate", "ky", "beta"]
    )
    print("Final values as a DataFrame: \n", final_values_df)
    final_values_df.set_index("ky", inplace=True)
    final_values_df.drop("beta", axis=1, inplace=True)
    final_values_df.sort_index(inplace=True)
    final_values_df.plot()
    plt.show()


if __name__ == "__main__":
    main()

# todo:
# this still only plots vs. the ky values,
# since it's assuming it's ky that is being altered.
# Since this won't be the case, I need to alter this to
# allow for the user to tweak which parameter is being examined,
# and plot how the values of frequency and growth rate
# change with respect to whatever parameter is being changed.
