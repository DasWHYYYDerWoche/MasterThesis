from os import mkdir
from typing import Optional
import numpy as np
import random
from deap import base, creator, tools, algorithms
from datetime import datetime
import pandas as pd
from pathlib import Path
import pickle

from ..Constants import JOINT_TYPES_5
from ..Simulator import SimulatorHandler
from ..Structs import Joint, Hyperparameters
from ..Utils import ExperimentMode, SimulationParameters
from .Parameter import Parameter

import logging
logger = logging.getLogger("global_logger")

class SimOptimizer:
    def __init__(self,
                 parameters : list[Parameter],
                 hyperparameters: Hyperparameters,
                 sim_handler : SimulatorHandler,
                 training_data : list[tuple[str, Optional[str], Optional[int]]] = None,
                 test_data : list[tuple[str, Optional[str], Optional[int]]] = None):
        # variables keeping track of optimized attributes
        self._parameters = parameters

        self._training_data = training_data
        self._test_data = test_data

        self._hyperparameters = hyperparameters
        self._sim_handler = sim_handler

        self._toolbox = base.Toolbox()
        self._create_classes()
        self._init_toolbox()

        self._logbook = None
        self._hall_of_fame = None
        self._stats = None
        self._run_identifier = ""
        self._test_results = []

    def _create_classes(self):
        if not hasattr(creator, "FitnessMin"):
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMin)

    def _init_toolbox(self):
        # creates a method attr_name for each attribute that samples a random value from their within its boundaries
        #global parameters
        for parameter in self._parameters:
            self._toolbox.register(parameter.identifier() + "_init", parameter.get_random_initial_value)  # creates a method to create new Individuals by calling tools.initCycle(creator.Individual, [list of methods], n=1)
        # tools.initCycle calls the methods in the list in order, repeating n times
        # creator.Individual is a container the results are put into
        self._toolbox.register(
            "individual",
            tools.initCycle,
            creator.Individual,
            [self._toolbox.__getattribute__(parameter.identifier() + "_init") for parameter in self._parameters],
            n=1,
        )
        # creates a method to create a new population by calling tools.initRepeat(list, self._toolbox.individual, n)
        # tools.initRepeat repeatedly calls the given method n times and puts the results into a container
        # since n isn't given, the resulting population method requires it as an argument
        self._toolbox.register("population", tools.initRepeat, list, self._toolbox.individual)

        # creates a new method called evaluate based on the evaluate method above this class
        # prefills the given parameters, so only requires the individual
        self._toolbox.register("evaluate", SimOptimizer.evaluate,
                               self._training_data, self._sim_handler, self._parameters)

        def mate(individual1, individual2):
            i1, i2 = tools.cxBlend(individual1, individual2, alpha = 0.5)
            SimOptimizer._clamp_individual(i1, [(p.lower_bound, p.upper_bound) for p in self._parameters])
            SimOptimizer._clamp_individual(i2, [(p.lower_bound, p.upper_bound) for p in self._parameters])
            return i1,i2

        def mutate(individual):
            tools.mutGaussian(individual,
                              mu=0,
                              sigma=[p.mutate_sigma for p in self._parameters],
                              indpb=self._hyperparameters.mutation_ind_pb)
            SimOptimizer._clamp_individual(individual, [(p.lower_bound, p.upper_bound) for p in self._parameters])
            return (individual,)

        # genetic operators to create new individuals
        self._toolbox.register("mate", mate)
        self._toolbox.register("mutate", mutate)
        self._toolbox.register("select", tools.selTournament, tournsize=self._hyperparameters.tournament_size)

    def _create_stats(self):
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)
        stats.register("std", np.std)
        return stats

    def run(self, seed: int = None, checkpoint_directory: Optional[Path] = None):
        self._run_identifier = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        print("start time: " + self._run_identifier)

        random.seed(seed)
        np.random.seed(seed)

        population = self._toolbox.population(n=self._hyperparameters.pop_size)

        stats = self._create_stats()
        hall_of_fame = tools.HallOfFame(5)

        if checkpoint_directory is not None:
            checkpoint_directory = Path(checkpoint_directory) / self._run_identifier
            checkpoint_directory.mkdir(parents=True, exist_ok=True)

        population, logbook = ea_simple_with_checkpoints(
            population=population,
            toolbox=self._toolbox,
            stats=stats,
            halloffame=hall_of_fame,
            cxpb=self._hyperparameters.crossover_pb,
            mutpb=self._hyperparameters.mutation_pb,
            ngen=self._hyperparameters.num_gen,
            checkpoint_interval=10,
            checkpoint_directory=checkpoint_directory,
            checkpoint_prefix="checkpoint_gen",
            verbose=True
        )

        self._logbook = logbook
        self._stats = stats
        self._hall_of_fame = hall_of_fame

        self._test_results.clear()

        for individual in self._hall_of_fame:
            self._test_results.append(
                float(
                    self.evaluate(
                        self._test_data,
                        self._sim_handler,
                        self._parameters,
                        individual
                    )[0]
                )
            )

        print("end time: " + datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

    def save_last_run(self, directory : Path):
        full_path = directory / self._run_identifier
        if not full_path.exists():
            full_path.mkdir(parents=True)
        df = pd.DataFrame(self._logbook)
        df.to_csv(full_path / "logbook.csv", index=False)

        df = pd.DataFrame(self._hall_of_fame)
        df.columns = [parameter.identifier() for parameter in self._parameters]
        df.insert(len(df.columns), "test results", self._test_results)
        df.to_csv(full_path / "hallOfFame.csv", index=False)

        f = None
        try:
            f = open(full_path / "Hyperparameters.txt", "w")
            f.write(self._hyperparameters.__str__())
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    # -------- static methods --------

    @staticmethod
    def evaluate(experiments: Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]],
                 simulator: SimulatorHandler,
                 parameters : list[Parameter],
                 individual) -> tuple[float]:
        """
        Maps individual genes to simulator parameters,
        runs simulation, and returns objective value.
        """
        # create simulation parameters

        simulator_parameters = SimulationParameters("")
        simulator_parameters.load_max_velocity()
        simulator_parameters.load_max_force(2.2)
        for parameter, value in zip(parameters, individual):
            parameter.set(value, simulator_parameters)
        gap_handler = simulator.simulation_gap(simulator_parameters,
                                               experiments,
                                               replay_mode=ExperimentMode.DEL_EXISTING)
        gap = gap_handler.get_optimization_target()
        # Return tuple because DEAP needs it
        return (gap,)

    @staticmethod
    def _clamp_individual(individual, bounds : list[tuple[float,float]]):
        for i, (low, high) in enumerate(bounds):
            if individual[i] < low:
                individual[i] = low
            elif individual[i] > high:
                individual[i] = high

    @property
    def hyperparameters(self):
        return self._hyperparameters

    def save_checkpoint(self,
            generation,
            population,
            halloffame,
            logbook,
            filename=None
    ):
        if filename is None:
            filename = f"checkpoint_gen_{generation}.pkl"
        checkpoint = {
            "generation": generation,
            "population": population,
            "halloffame": halloffame,
            "logbook": logbook,
            "rndstate": random.getstate(),
        }
        with open(filename, "wb") as f:
            pickle.dump(checkpoint, f)
        print(f"Saved checkpoint: {filename}")

    def load_checkpoint(self, filename: Path, checkpoint_directory: Optional[Path] = None):
        filename = Path(filename)
        with open(filename, "rb") as f:
            checkpoint = pickle.load(f)
        random.setstate(checkpoint["rndstate"])
        if "np_rndstate" in checkpoint:
            np.random.set_state(checkpoint["np_rndstate"])
        population = checkpoint["population"]
        halloffame = checkpoint["halloffame"]
        logbook = checkpoint["logbook"]
        start_gen = checkpoint["generation"]
        stats = self._create_stats()
        if checkpoint_directory is not None:
            checkpoint_directory = Path(checkpoint_directory)
            checkpoint_directory.mkdir(parents=True, exist_ok=True)
        else:
            checkpoint_directory = filename.parent
        final_population, logbook = ea_simple_with_checkpoints(
            population=population,
            toolbox=self._toolbox,
            cxpb=self._hyperparameters.crossover_pb,
            mutpb=self._hyperparameters.mutation_pb,
            ngen=self._hyperparameters.num_gen,
            stats=stats,
            halloffame=halloffame,
            logbook=logbook,
            start_gen=start_gen,
            verbose=True,
            checkpoint_interval=10,
            checkpoint_directory=checkpoint_directory,
            checkpoint_prefix="checkpoint_gen"
        )

        self._logbook = logbook
        self._stats = stats
        self._hall_of_fame = halloffame

        self._test_results.clear()

        for individual in self._hall_of_fame:
            self._test_results.append(
                float(
                    self.evaluate(
                        self._test_data,
                        self._sim_handler,
                        self._parameters,
                        individual
                    )[0]
                )
            )

        return final_population, logbook


def ea_simple_with_checkpoints(
    population,
    toolbox,
    cxpb,
    mutpb,
    ngen,
    stats=None,
    halloffame=None,
    logbook=None,
    start_gen=0,
    verbose=True,
    checkpoint_interval=10,
    checkpoint_directory: Optional[Path] = None,
    checkpoint_prefix="checkpoint_gen"
):
    if checkpoint_directory is not None:
        checkpoint_directory = Path(checkpoint_directory)
        checkpoint_directory.mkdir(parents=True, exist_ok=True)

    if logbook is None:
        logbook = tools.Logbook()
        logbook.header = ["gen", "nevals"] + (stats.fields if stats else [])

    if not hasattr(logbook, "header") or logbook.header is None:
        logbook.header = ["gen", "nevals"] + (stats.fields if stats else [])

    # Evaluate invalid individuals
    invalid_individuals = [
        ind for ind in population if not ind.fitness.valid
    ]

    fitnesses = map(toolbox.evaluate, invalid_individuals)

    for ind, fit in zip(invalid_individuals, fitnesses):
        ind.fitness.values = fit

    # Fresh run: record generation 0
    if start_gen == 0:
        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats is not None else {}

        logbook.record(
            gen=0,
            nevals=len(invalid_individuals),
            **record
        )

        if verbose:
            print(logbook.stream)

    # Resumed run
    else:
        if halloffame is not None and len(invalid_individuals) > 0:
            halloffame.update(population)

        if verbose:
            print(f"Resuming evolution from generation {start_gen}")

    # Nothing to do if checkpoint is already at or after target generation
    if start_gen >= ngen:
        if verbose:
            print(
                f"Checkpoint generation {start_gen} is already >= target generation {ngen}. "
                "No additional evolution performed."
            )

        return population, logbook

    for gen in range(start_gen + 1, ngen + 1):

        # Selection
        offspring = toolbox.select(population, len(population))

        # Variation
        offspring = algorithms.varAnd(
            offspring,
            toolbox,
            cxpb=cxpb,
            mutpb=mutpb
        )

        # Evaluate invalid offspring
        invalid_individuals = [
            ind for ind in offspring if not ind.fitness.valid
        ]

        fitnesses = map(toolbox.evaluate, invalid_individuals)

        for ind, fit in zip(invalid_individuals, fitnesses):
            ind.fitness.values = fit

        # Update hall of fame
        if halloffame is not None:
            halloffame.update(offspring)

        # Replace population
        population[:] = offspring

        # Record stats
        record = stats.compile(population) if stats is not None else {}

        logbook.record(
            gen=gen,
            nevals=len(invalid_individuals),
            **record
        )

        if verbose:
            print(logbook.stream)

        # Save checkpoint
        if checkpoint_interval is not None and gen % checkpoint_interval == 0:
            filename = f"{checkpoint_prefix}_{gen}.pkl"

            if checkpoint_directory is not None:
                filename = checkpoint_directory / filename

            save_checkpoint(
                generation=gen,
                population=population,
                halloffame=halloffame,
                logbook=logbook,
                filename=filename
            )

    return population, logbook

def save_checkpoint(
    generation,
    population,
    halloffame,
    logbook,
    filename=None
):
    if filename is None:
        filename = f"checkpoint_gen_{generation}.pkl"

    filename = Path(filename)

    if filename.parent is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "generation": generation,
        "population": population,
        "halloffame": halloffame,
        "logbook": logbook,
        "rndstate": random.getstate(),
        "np_rndstate": np.random.get_state(),
    }

    with open(filename, "wb") as f:
        pickle.dump(checkpoint, f)

    print(f"Saved checkpoint: {filename}")