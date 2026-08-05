"""
My name is Plotter, Harry Plotter
"""
from ..Constants import PATH_OUTPUT
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.cbook import boxplot_stats
import pandas as pd

def linear_plot(x : list[float], y : list[float], x_label : str, y_label : str, path : str, y_margin : float = 0.05, h_line : Optional[float] = None, h_line_legend : Optional[str] = None):
    min_y = min(y)
    max_y = max(y)
    min_x = x[y.index(min_y)]
    plt.rcParams.update({
        "text.usetex": True,
        "font.size": 12,
        "font.family": "serif",
        "text.latex.preamble": r"""
            \usepackage{libertine}
            \usepackage[libertine]{newtxmath}
        """
    })
    plt.figure(figsize=(6.06, 2.5))
    plt.plot(x, y, marker='o')
    plt.plot(min_x, min_y, marker='o', label="Minimum: (" + str(min_x) + ", " + str(round(min_y, 3)) + ")")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.ylim(-y_margin * max_y, (y_margin +1) * max_y)
    if h_line and h_line_legend:
        plt.axhline(
            y=float(h_line),
            color="red",
            linestyle="--",
            linewidth=0.5,
            label=h_line_legend + str(round(h_line, 3))
        )
    plt.grid(True)
    plt.legend()
    plt.savefig(PATH_OUTPUT / path, bbox_inches='tight')


#def action_boxplot(data : dict[str, list[float]], y_margin : float = 0.05)


def boxplot(data : dict[str, list[float]], mean_data : dict[str,float],
            x_label : str, y_label : str, path : str,
            y_margin : float = 0.05,
            h_line : Optional[float] = None, h_line_legend : Optional[str] = None,
            boxplot_sensors : Optional[list[str]] = None):
    plt.rcParams.update({
        "text.usetex": True,
        "font.size": 12,
        "font.family": "serif",
        "text.latex.preamble": r"""
                \usepackage{libertine}
                \usepackage[libertine]{newtxmath}
            """
    })

    if boxplot_sensors:
        drawing_data = {key: value for key,value in data.items() if key in boxplot_sensors}
    else:
        drawing_data = data
    max_y = max([max(value) for value in drawing_data.values()])
    min_y = min([min(value) for value in drawing_data.values()])
    min_y = min(min_y, 0)
    max_y = max(max_y, 0)
    plt.figure(figsize=(6.06, 2.5))
    plt.boxplot(
        drawing_data.values(),
        labels=drawing_data.keys(),
        showfliers=True
    )
    plt.grid(visible=True, axis="y")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.ylim(min_y+(y_margin * min_y), (y_margin*max_y)+max_y)
    #plt.ylim(-1, 1.5)
    if h_line and h_line_legend:
        plt.axhline(
            y=float(h_line),
            color="red",
            linestyle="--",
            linewidth=0.5,
            label=h_line_legend + str(round(h_line, 3))
        )
    plt.grid(visible=True, axis="y")
    #plt.legend() #loc="lower left"
    plt.savefig(PATH_OUTPUT / "images" / (path + ".pdf"), bbox_inches='tight')

    stats = boxplot_stats(data.values(),labels=data.keys())
    # Convert to table
    table = pd.DataFrame([
        {
            "Label": s["label"],
            "Lower whisker": round(s["whislo"], 3),
            "Q1 / lower box": round(s["q1"], 3),
            "Median": round(s["med"], 3),
            "Weighted Mean": round(mean, 3),
            "Q3 / upper box": round(s["q3"], 3),
            "Upper whisker": round(s["whishi"], 3)
        }
        for s, mean in zip(stats, mean_data.values())
    ])
    table.to_csv(PATH_OUTPUT / "csvs"/(path +".csv"), index=False)

