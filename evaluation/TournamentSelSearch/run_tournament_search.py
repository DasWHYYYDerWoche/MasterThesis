import matplotlib.pyplot as plt
y_margin = 0.05
x = [2,3,4,5,6]
y = [0.01920208329362875,0.01983121657760712,0.02002585946265589, 0.02075403115647153, 0.019361043603321196]
y = [value / 0.05307869684668788  for value in y]
min_y = min(y)
min_x = x[y.index(min_y)]
max_y = max(y)
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
plt.xlabel("Tournament Size")
plt.ylabel("Simulation Gap")
plt.ylim(- y_margin * max_y,(y_margin +1)* max_y)
plt.grid(True)
plt.savefig("outputTournamentSizeSearch.pdf", bbox_inches='tight')