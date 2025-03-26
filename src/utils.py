import os
import traceback
import pandas as pd
import numpy as np


def parse_row_data(input_path, output_path, column_names, number_of_ignore_lines=0):
    names = [name for name in os.listdir(input_path)]

    for name in names:
        try:
            with open(f"{input_path}/{name}", "r", encoding="utf-8") as infile, \
                    open(f"{output_path}/{name[:-4]}.csv", "w", encoding="utf-8") as outfile:
                outfile.write(column_names + "\n")

                if number_of_ignore_lines > 0:
                    for _ in range(number_of_ignore_lines):
                        next(infile, None)

                for line in infile:
                    line = line.replace("	", ",")
                    outfile.write(line)
        except Exception as e:
            print(f"Error with file {name}: {str(e)}")
            traceback.print_exc()


def process_data(path_to_data, data_type):
    if data_type == "capture_map":
        return process_capture_map_data(path_to_data)
    elif data_type == "vac":
        return process_VAC_data(path_to_data)
    else:
        print("Wrong parsed_data type")


def process_capture_map_data(path_to_data):
    names = [name for name in os.listdir(path_to_data)]

    result_df = pd.DataFrame(columns=["title", "mean", "std", "var"])
    result_df = result_df.astype({"title": "str", "mean": "float64", "std": "float64", "var": "float64"})

    for name in names:
        df = pd.read_csv(f"{path_to_data}/{name}")
        df.drop(columns=["delme"], inplace=True)
        mean = np.mean(df['B'])
        std = np.std(df['B'])
        var = np.var(df['B'])
        result_df = pd.concat([
            result_df,
            pd.DataFrame({
                "title": [name.split()[1][6:13]],
                "mean": [mean],
                "std": [std],
                "var": [var]
            }
            )], ignore_index=True)
    return result_df


def process_VAC_data(path_to_data):
    lower_boundary = 0.1e-6
    upper_boundary = 1e-6

    names = [name for name in os.listdir(path_to_data)]

    result_df = pd.DataFrame(columns=["title", "angle", "slope", "intercept", ])
    result_df = result_df.astype({"title": "str", "angle": "float64", "slope": "float64", "intercept": "float64"})

    for name in names:
        df = pd.read_csv(f"{path_to_data}/{name}")
        df.drop(columns=["delme"], inplace=True)
        df = df[(df['U'] >= lower_boundary) & (df['U'] <= upper_boundary)]
        log_df = pd.DataFrame({
            'log_I': np.log10(df['I']),
            'log_U': np.log10(df['U'])
        })
        coefficients = np.polyfit(log_df['log_I'], log_df['log_U'], 1)
        slope = coefficients[0]
        intercept = coefficients[1]
        angle = np.degrees(np.arctan(slope))
        result_df = pd.concat([
            result_df,
            pd.DataFrame({
                "title": [name[11:18]],
                "angle": [angle],
                "slope": [slope],
                "intercept": [intercept]
            })
        ])

    return result_df


# TODO each VAC must have equal amount of lines, remove negative values
def new_process_vac(path_to_data):
    names = [name for name in os.listdir(path_to_data)]

    result_df = pd.DataFrame(columns=["title", "I, A", "U, V"])
    result_df = result_df.astype({"title": "str", "I, A": "float64", "U, V": "float64"})

    for name in names:
        df = pd.read_csv(f"{path_to_data}/{name}")
        df.drop(columns=["delme"], inplace=True)
        df.insert(0, "title", name[11:18])
        result_df = pd.concat([
            result_df,
            pd.DataFrame({
                "title": df['title'],
                "I, A": df['I'],
                "U, V": df['U'],
            })
        ])

    return result_df


# TODO each capture map must have equal amount of lines, remove negative values
def new_process_capture_map(path_to_data):
    names = [name for name in os.listdir(path_to_data)]

    result_df = pd.DataFrame(columns=["title", "x, mm", "y, mm", "B, mT"])
    result_df = result_df.astype({"title": "str", "x, mm": "float64", "y, mm": "float64", "B, mT": "float64"})

    for name in names:
        df = pd.read_csv(f"{path_to_data}/{name}")
        df.drop(columns=["delme"], inplace=True)
        name_to_insert = name.split()[1][6:13]
        df.insert(0, "title", name_to_insert)
        result_df = pd.concat([
            result_df,
            pd.DataFrame({
                "title": df['title'],
                "x, mm": df['x'],
                "y, mm": df['y'],
                "B, mT": df['B'],
            })
        ])

    return result_df
