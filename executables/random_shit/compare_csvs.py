from fileinput import filename

import pandas as pd
import numpy as np
import os

# tolerance settings
rtol = 1e-5
atol = 1e-8

my_pc = "paramSet_default_mypc"
uni_pc = "paramSet_default_unipc"

my_actions = [f for f in os.listdir(my_pc)]
uni_actions = [f for f in os.listdir(uni_pc)]
common_actions = sorted(set(my_actions) & set(uni_actions))
summary = {action : [] for action in common_actions}

for action in common_actions:
    my_files = {filename.split("_")[0]: filename for filename in os.listdir(my_pc + "/" + action + "/260108") if filename.endswith(".csv")}
    uni_files = {filename.split("_")[0]: filename for filename in os.listdir(uni_pc + "/" + action + "/260108") if filename.endswith(".csv")}
    common_keys = sorted(set(my_files.keys()) & set(uni_files.keys()))
    for key in common_keys:
        my_file = my_files[key]
        uni_file = uni_files[key]
        my_path = my_pc + "/" + action + "/260108/" + my_file
        uni_path = uni_pc + "/" + action + "/260108/" + uni_file

        df1 = pd.read_csv(my_path, sep=";")
        df2 = pd.read_csv(uni_path, sep=";")
        # drop time column if present
        df1_cmp = df1.drop(columns=["time"], errors="ignore")
        df2_cmp = df2.drop(columns=["time"], errors="ignore")

        if df1_cmp.shape != df2_cmp.shape:
            print(f"Shape mismatch for prefix {key}, skipping")
            summary[action].append("Shape mismatch")
            continue

        int_diff = (df1_cmp != df2_cmp).astype(int)
        identical = int_diff.to_numpy().sum() == 0
        if identical:
            summary[action].append("Identical")
            continue
        float_close = np.isclose(df1_cmp, df2_cmp, rtol=rtol, atol=atol)
        if float_close.all():
            summary[action].append("Float Close")
            continue
        summary[action].append("Different")


# write summary file
df = pd.DataFrame({k: pd.Series(v) for k, v in summary.items()})
df.to_csv("comparison_summary.csv", index=True, sep=";")

print("Done.")