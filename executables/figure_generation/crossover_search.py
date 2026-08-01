import pandas as pd
import numpy as np
from src import PATH_INPUT,PATH_OUTPUT, linear_plot

df = pd.read_csv(PATH_OUTPUT / "normalization_factors.csv")
scale_factor = df["scale"].iloc[0]
search_results = {}
for crossover_probability in [0.5,0.6,0.7,0.8,0.9]:
    sim_gaps = pd.read_csv(PATH_INPUT / "crossover_probability_search" /
                                                  ("cxpb" +str(crossover_probability) +  "_hallOfFame.csv"))["test results"].tolist()
    search_results[crossover_probability] = np.min(sim_gaps) / scale_factor
print(search_results)
linear_plot(
    x=list(search_results.keys()),
    y=list(search_results.values()),
x_label="Crossover Probability", y_label="Simulation Gap", path="images/crossover_probability_search.pdf")