import random
import numpy as np
from deap import base, creator, tools, algorithms

# ============================================
# Configuration
# ============================================

# Parameter bounds (adjust as needed)
BOUNDS = {
    "kd": (0.0, 100.0),
    "kp": (0.0, 100.0),
    "contactKd": (0.0, 100.0),
    "contactKp": (0.0, 100.0),
    "p1": (-10.0, 10.0),
    "p2": (-10.0, 10.0),
    "p3": (-10.0, 10.0),
    "p4": (-10.0, 10.0),
    "p5": (-10.0, 10.0),
}

PARAM_NAMES = list(BOUNDS.keys())
DIM = len(PARAM_NAMES)

# ============================================
# DEAP Setup
# ============================================

# Minimize objective
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Attribute generator: random value within bounds
def random_param(low, high):
    return random.uniform(low, high)

# Register each parameter generator
for name in PARAM_NAMES:
    low, high = BOUNDS[name]
    toolbox.register(f"attr_{name}", random_param, low, high)

# Structure initializers
toolbox.register(
    "individual",
    tools.initCycle,
    creator.Individual,
    [toolbox.__getattribute__(f"attr_{name}") for name in PARAM_NAMES],
    n=1,
)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# ============================================
# Evaluation Function
# ============================================

def evaluate(individual):
    """
    Maps individual genes to simulator parameters,
    runs simulation, and returns objective value.
    """
    # Map parameters
    for i, name in enumerate(PARAM_NAMES):
        setter = getattr(sim, f"set_{name}")
        setter(individual[i])

    # Run simulation
    objective = sim.run()

    # Return tuple (DEAP requirement)
    return (objective,)

toolbox.register("evaluate", evaluate)

# ============================================
# Genetic Operators
# ============================================

toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=5.0, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# ============================================
# Main Optimization Loop
# ============================================

def main():
    random.seed(42)

    population = toolbox.population(n=50)
    ngen = 40
    cxpb = 0.6
    mutpb = 0.3

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    halloffame = tools.HallOfFame(1)

    population, logbook = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=cxpb,
        mutpb=mutpb,
        ngen=ngen)

    best = tools.selBest(population, k=1)[0]

    print("\nBest Individual:")
    for i, name in enumerate(PARAM_NAMES):
        print(f"{name}: {best[i]}")

    print(f"Best Objective Value: {best.fitness.values[0]}")

    return best


if __name__ == "__main__":
    best_solution = main()