from os import mkdir
from typing import Optional
import numpy as np
import random
from deap import base, creator, tools, algorithms
from datetime import datetime
import pandas as pd
from pathlib import Path

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
        # create classes given a name, a baseclass and arguments given to the class during creation
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

    def _init_toolbox(self):
        # creates a method attr_name for each attribute that samples a random value from their within its boundaries
        #global parameters
        for parameter in self._parameters:
            # creates a method to fill the parameter with an initial value
            self._toolbox.register(parameter.identifier() + "_init", parameter.get_random_initial_value)
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

        def select(individuals):
            pop = tools.selBest(individuals, 2)
            pop += tools.selTournament(individuals, k= len(individuals) - 2, tournsize=self._hyperparameters.tournament_size)

        # genetic operators to create new individuals
        self._toolbox.register("mate", mate)
        self._toolbox.register("mutate", mutate)
        self._toolbox.register("select", select)

    def run(self, seed : int = None):
        self._run_identifier = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        print("start time: " + self._run_identifier)
        random.seed(seed)
        population = self._toolbox.population(n=self._hyperparameters.pop_size)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)
        stats.register("std", np.std)

        hall_of_fame = tools.HallOfFame(5)

        population, logbook = algorithms.eaSimple(
            population,
            self._toolbox,
            stats=stats,
            halloffame=hall_of_fame,
            cxpb=self._hyperparameters.crossover_pb,
            mutpb=self._hyperparameters.mutation_pb,
            ngen=self._hyperparameters.num_gen)
        self._logbook = logbook
        self._stats = stats
        self._hall_of_fame = hall_of_fame
        self._test_results.clear()
        for individual in self._hall_of_fame:
            self._test_results.append(float(self.evaluate(
                self._test_data, self._sim_handler, self._parameters, individual)
                                            [0]))
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
        simulator_parameters = SimulationParameters("", "max_force_2.1")
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