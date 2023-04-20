import os
import sys
import json
import numpy as np
import pandas as pd


from matplotlib import pyplot as plt


def rename_column(df, old_name, new_name):
    df.rename(columns={old_name: new_name}, inplace=True)
    return df[new_name]


def overwrite_with_gen(df, gen_df, column_name, gen_column_name):
    df[column_name] = gen_df[gen_column_name]
    return df[column_name]


def saturate_on_full(df, column_name, saturate_ranges_path):
    if saturate_ranges_path != None:
        # Saturate ranges is a json file with the ranges to saturate
        with open(saturate_ranges_path) as saturate_file:
            saturate_dict = json.load(saturate_file)
            if column_name in saturate_dict.keys():
                ranges = saturate_dict[column_name]
                min = ranges[0]
                max = ranges[1]
                val = df[column_name].values
                saturated = np.where(val < min, min, val)
                saturated = np.where(saturated > max, max, saturated)
                df[column_name] = saturated
    return df[column_name]


def pi_minuspi_periodicity(df, column_name):
    df[column_name] = np.where(
        df[column_name] < -np.pi, df[column_name] + 2 * np.pi, df[column_name]
    )
    df[column_name] = np.where(
        df[column_name] > np.pi, df[column_name] - 2 * np.pi, df[column_name]
    )
    return df[column_name]


def multiply_by_gen(df, gen_df, column_name, gen_column_name):
    print("Multiplied!")
    print(df[column_name])
    df[column_name] = df[column_name] * gen_df[gen_column_name]
    print(df[column_name])
    return df[column_name]


def add_gen(df, gen_df, column_name, gen_column_name):
    df[column_name] = df[column_name] + gen_df[gen_column_name]
    return df[column_name]


def restore_range(column_name, scale_dict, df):
    """
    Restore data range to the original value before dividing by max
    """
    scale = scale_dict[column_name]
    df[column_name] = df[column_name] * scale
    return df[column_name]


def inverse_transform(df, column_name, function, p):
    df[column_name] = df[column_name].apply(lambda x: (function(x) - p[1]) / p[0])
    return df[column_name]


def unsmearing(df, column_name, interval, value):
    """Unsmearing for in variables. We have gaussian and uniform smearing.
    If we have interval, that means that we built a fake gaussian dataset
    in the selected interval, and then we just have to compute the sample mean
    in this range.
    """
    val = df[column_name].values
    if interval != None:
        mask_condition = np.logical_and(val >= interval[0], val <= interval[1])

        # Assuming that the value to be unsmeared is always np.log(1e-3),
        # which corresponds to an int value of 0 after a np.log(x + 1e-3)
        # transformation
        val[mask_condition] = value

    else:
        df[column_name] = np.rint(df[column_name].values)
    return df[column_name]


def cut_unsmearing(df, column_name, cut, x1, x2):
    val = df[column_name].values
    df[column_name] = np.where(val < cut, x1, x2)
    return df[column_name]


def process_column_var(column_name, operations, df, gen_df, saturate_ranges_path=None):
    for i, op in enumerate(operations):
        if op[0] == "d":
            mask_condition = op[1]
            value = op[2]
            df[column_name] = unsmearing(df, column_name, mask_condition, value)

        elif op[0] == "c":
            cut = op[1]
            vals = op[2]
            df[column_name] = cut_unsmearing(df, column_name, cut, *vals)

        elif op[0] == "i":
            function = op[1]
            p = op[2]
            df[column_name] = inverse_transform(df, column_name, function, p)

        elif op[0] == "m":
            gen_column_name = op[1]
            df[column_name] = multiply_by_gen(df, gen_df, column_name, gen_column_name)

        elif op[0] == "a":
            gen_column_name = op[1]
            df[column_name] = add_gen(df, gen_df, column_name, gen_column_name)

        elif op[0] == "s":
            df[column_name] = saturate_on_full(df, column_name, saturate_ranges_path)

        elif op[0] == "pmp":
            df[column_name] = pi_minuspi_periodicity(df, column_name)

        elif op[0] == "genow":
            gen_column_name = op[1]
            df[column_name] = overwrite_with_gen(
                df, gen_df, column_name, gen_column_name
            )
        elif op[0] == "rename":
            if i != len(operations) - 1:
                raise ValueError(
                    "Rename operation must be the last operation in the list"
                )
            new_name = op[1]
            df[column_name] = rename_column(df, column_name, new_name)
        else:
            pass
    return df[column_name]


def postprocessing(
    df, gen_df, vars_dictionary, scale_file_path=None, saturate_ranges_path=None
):
    """
    Postprocessing general function given any dataframe and its dictionary
    """
    if scale_file_path != None:
        with open(scale_file_path) as scale_file:
            scale_dict = json.load(scale_file)

    for column_name, operation in vars_dictionary.items():
        if scale_file_path != None:
            if column_name in scale_dict.keys():
                df[column_name] = restore_range(column_name, scale_dict, df)
        df[column_name] = process_column_var(
            column_name, operation, df, gen_df, saturate_ranges_path
        )

    return df
