"""
My name is Plotter, Harry Plotter
"""

from ..Constants import PATH_OUTPUT

import matplotlib.pyplot as plt

y_margin = 0.05
x = [0.5,0.6,0.7,0.8,0.9]
y = [0.029018217132860208,0.022002075824397144,0.021266958970790843, 0.019962063085827954, 0.020467705718168222]
y = [value / 0.05307869684668788 for value in y]

def linear_plot(x : list[float], y : list[float], x_label : str, y_label : str, path : str, y_margin : float = 0.05):
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
    plt.plot(min_x, min_y, marker='o')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.ylim(-y_margin * max_y, (y_margin +1) * max_y)
    plt.grid(True)
    plt.savefig(PATH_OUTPUT / path, bbox_inches='tight')