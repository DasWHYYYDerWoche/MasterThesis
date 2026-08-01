import pandas as pd
import numpy as np
from src import PATH_INPUT,PATH_OUTPUT, linear_plot

df = pd.read_csv(PATH_OUTPUT / "normalization_factors.csv")
scale_factor = df["scale"].iloc[0]
search_results = {}
for tournament_size in [2,3,4,5,6]:
    sim_gaps = pd.read_csv(PATH_INPUT / "tournament_size_search" /
                                                  ("ts" +str(tournament_size) +  "_hallOfFame.csv"))["test results"].tolist()
    search_results[tournament_size] = np.min(sim_gaps) / scale_factor
print(search_results)
linear_plot(
    x=list(search_results.keys()),
    y=list(search_results.values()),
x_label="Tournament Size", y_label="Simulation Gap", path="images/tournament_size_search.pdf")