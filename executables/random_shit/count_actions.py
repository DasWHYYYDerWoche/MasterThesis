import pandas as pd
import numpy as np
import os
from src import *


#summary = {action : [] for action in actions}
dates = ["260528_0", "260528_1", "260529_0", "260529_1"]
total_28 = {}
total_29 = {}


train_28_per_action = {}
train_29_per_action = {}
test_28_per_action = {}
test_29_per_action = {}
for folder in [f for f in PATH_FIELD_LOGS.iterdir()]:
    if folder.name == "calculate_statistics":
        continue
    if folder.name not in total_28.keys():
        total_28[folder.name] = 0
    if folder.name not in total_29.keys():
        total_29[folder.name] = 0
    total_28[folder.name] += len(list((folder / "260528_0").iterdir()))
    total_28[folder.name] += len(list((folder / "260528_1").iterdir()))

    total_29[folder.name] += len(list((folder / "260529_0").iterdir()))
    total_29[folder.name] += len(list((folder / "260529_1").iterdir()))

train_28 = {key : round(value * 0.8) for key,value in total_28.items()}
test_28 = {key :  total - train for (key, train),total in zip(train_28.items(), total_28.values())}

train_29 = {key : round(value * 0.8) for key,value in total_29.items()}
test_29 = {key :  total - train for (key, train),total in zip(train_29.items(), total_29.values())}

test_totals = {key :  t_29 + t_28 for (key, t_29),t_28 in zip(test_29.items(), test_28.values())}
test_total = sum(test_totals.values())
train_totals = {key :  t_29 + t_28 for (key, t_29),t_28 in zip(train_29.items(), train_28.values())}
train_total = sum(train_totals.values())

print("total 28:")
print(str(total_28))
print(str(train_28))
print(str(test_28))

print("total 29:")
print(str(total_29))
print(str(train_29))
print(str(test_29))

print("test total:")
print(str(test_totals))
print(str(test_total))

print("train total:")
print(str(train_totals))
print(str(train_total))