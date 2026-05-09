from os import mkdir
from typing import Optional
import numpy as np
import random
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from datetime import datetime
import pandas as pd
import os
from pathlib import Path

from ..Constants import JOINT_TYPES
from ..Simulator import SimulatorHandler
from ..Structs import Joint
from ..Utils import SimulationGapHandler, SimulationGapData, ExperimentMode, SimulationParameters, ExperimentParameters

import logging
logger = logging.getLogger("global_logger")


class SimOptimizer:
    def __init__(self,
                 global_attributes : list[str],
                 per_joint_type_attributes : list[str],
                 training_data : list[tuple[str, Optional[str], Optional[int]]] = None,
                 test_data : list[tuple[str, Optional[str], Optional[int]]] = None,
                 population_size : int = 20,
                 max_gen : int = 100,
                 crossover_pb : float = 0.5,
                 mutation_pb : float = 0.2):
        self._global_attributes = global_attributes
        self._global_attribute_names = []
        self._global_attribute_boundaries = []
        self._per_joint_type_attributes = per_joint_type_attributes
        self._per_joint_type_attribute_names = []
        self._per_joint_type_attribute_boundaries = []
        self._individual_dimension = len(global_attributes) + (5 * len(per_joint_type_attributes))
        self._training_data = training_data
        self._test_data = test_data

        self._initialization_offset = 0.1
        self._lower_bound_factor = 0.001
        self._upper_bound_factor = 100

        self._population_size = population_size
        self._crossover_pb = crossover_pb
        self._mutation_pb = mutation_pb
        self._max_gen = max_gen

        self._simulator = SimulatorHandler()
        self._simulator.num_instances = 10
        self._simulator.replays_per_instance = 8
        self._simulator.show_ui = False

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
        for attribute_name in self._global_attributes:
            value = self._simulator.get_default_value(attribute_name)
            if type(value) is None:
                logger.error("Global Parameter %s was not found", attribute_name)
            identifier = f"g_{attribute_name}"
            self._global_attribute_names.append(identifier)
            self._global_attribute_boundaries.append((value * self._lower_bound_factor, value * self._upper_bound_factor))
            self._toolbox.register(identifier, random.uniform, value * (1 - self._initialization_offset), value * (1 + self._initialization_offset))
        #per-joint-type parameters
        for attribute_name in self._per_joint_type_attributes:
            for motor_index, joints_of_type in enumerate(JOINT_TYPES.values()):
                example_joint = joints_of_type[0]
                joint_object = self._simulator.get_default_value(example_joint)
                if type(joint_object) is not Joint:
                    logger.error("Per Joint Type %s was not found", attribute_name)
                value = getattr(joint_object, attribute_name, None)
                if value is None:
                    logger.error("Attribute for %s did not exists in %s", attribute_name, joint_object.__name__)
                identifier = f"jt_{attribute_name}_{motor_index}"
                self._per_joint_type_attribute_names.append(identifier)
                self._per_joint_type_attribute_boundaries.append(
                    (value * self._lower_bound_factor, value * self._upper_bound_factor))
                self._toolbox.register(identifier, random.uniform, value * (1 - self._initialization_offset), value * (1 + self._initialization_offset))
        # creates a method to create new Individuals by calling tools.initCycle(creator.Individual, [list of methods], n=1)
        # tools.initCycle calls the methods in the list in order, repeating n times
        # creator.Individual is a container the results are put into
        self._toolbox.register(
            "individual",
            tools.initCycle,
            creator.Individual,
            [self._toolbox.__getattribute__(name) for name in self._global_attribute_names] +
            [self._toolbox.__getattribute__(name) for name in self._per_joint_type_attribute_names],
            n=1,
        )

        # creates a method to create a new population by calling tools.initRepeat(list, self._toolbox.individual, ?)
        # tools.initRepeat repeatedly calls the given method n times and puts the results into a container
        # since n isnt given, the resulting population method requires it as an argument
        self._toolbox.register("population", tools.initRepeat, list, self._toolbox.individual)

        # creates a new method called evaluate based on the evaluate method above this class
        # prefills the given parameters, so only requires the individual
        self._toolbox.register("evaluate", SimOptimizer.evaluate,
                               self._training_data, self._simulator, self._global_attribute_names, self._per_joint_type_attribute_names)

        def mate(individual1, individual2):
            i1, i2 = tools.cxBlend(individual1, individual2, alpha = 0.5)
            SimOptimizer.clamp(i1, self._global_attribute_boundaries + self._per_joint_type_attribute_boundaries)
            SimOptimizer.clamp(i2, self._global_attribute_boundaries + self._per_joint_type_attribute_boundaries)
            return i1,i2

        def mutate(individual):
            tools.mutGaussian(individual, mu=0, sigma=10.0, indpb=0.2),# TODO: add to hyperparameters
            SimOptimizer.clamp(individual, self._global_attribute_boundaries + self._per_joint_type_attribute_boundaries)
            return (individual,)

        # genetic operators to create new individuals
        self._toolbox.register("mate", mate)
        self._toolbox.register("mutate", mutate)
        self._toolbox.register("select", tools.selTournament, tournsize=3) #TODO: add to hyperparameters

    def run(self, seed : int = None):
        self._run_identifier = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        random.seed(seed)
        population = self._toolbox.population(n=self._population_size)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        halloffame = tools.HallOfFame(5)

        population, logbook = algorithms.eaSimple(
            population,
            self._toolbox,
            stats=stats,
            halloffame=halloffame,
            cxpb=self._crossover_pb,
            mutpb=self._mutation_pb,
            ngen=self._max_gen)
        self._logbook = logbook
        self._stats = stats
        self._hall_of_fame = halloffame
        self._test_results.clear()
        for individual in self._hall_of_fame:
            self._test_results.append(float(self.evaluate(
                self._test_data, self._simulator, self._global_attribute_names, self._per_joint_type_attribute_names, individual)
                                            [0]))
        return population, logbook, stats, halloffame

    def save_last_run(self, directory : Path):
        full_path = directory / self._run_identifier
        if not full_path.exists():
            full_path.mkdir(parents=True)
        df = pd.DataFrame(self._logbook)
        df.to_csv(full_path / "logbook", index=False)
        df = pd.DataFrame(self._hall_of_fame)
        df.columns = self._global_attribute_names + self._per_joint_type_attribute_names
        df.insert(len(df.columns), "test results", self._test_results)
        df.to_csv(full_path / "hallOfFame", index=False)
        text = ""
        text += "population_size =" + str(self._population_size) + "\n"
        text += "crossover_pb =" + str(self._crossover_pb) + "\n"
        text += "mutation_pb =" + str(self._mutation_pb) + "\n"
        text += "generations =" + str(self._max_gen) + "\n"
        text += "initialization_offset =" + str(self._initialization_offset) + "\n"
        f = None
        try:
            f = open(full_path / "Hyperparameters.txt", "w")
            f.write(text)
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    # -------- static methods --------

    @staticmethod
    def evaluate(experiments: Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]],
                 simulator: SimulatorHandler,
                 global_attribute_names: list[str],
                 per_joint_type_attribute_names: list[str],
                 individual) -> tuple[float]:
        """
        Maps individual genes to simulator parameters,
        runs simulation, and returns objective value.
        """
        # create simulation parameters
        simulator_parameters = SimulationParameters("")
        i = 0
        for name in global_attribute_names:
            setattr(simulator_parameters, name.split("_")[1], individual[i])
            i += 1

        for name in per_joint_type_attribute_names:
            split_name = name.split("_")
            name = split_name[1]
            joint_type = int(split_name[2])
            simulator_parameters.set_for_joint_type(joint_type, name, individual[i])
            i += 1

        # Run simulation
        gap_handler = simulator.simulation_gap(simulator_parameters, experiments,
                                               replay_mode=ExperimentMode.DEL_EXISTING)
        if len(gap_handler.invalid_logs) > 0:
            logger.warning("%s invalid logs found: ", len(gap_handler.invalid_logs), gap_handler.invalid_logs)
        gap = gap_handler.get_final_FINAL_gap_avg(lambda gap_object: SimulationGapData.get_total_gap_avg(gap_object))
        # Return tuple (DEAP requirement)
        return (gap,)

    @staticmethod
    def clamp(individual, bounds : list[tuple[float,float]]):
        for i, (low, high) in enumerate(bounds):
            if individual[i] < low:
                individual[i] = low
            elif individual[i] > high:
                individual[i] = high

    @property
    def population_size(self) -> int:
        return self._population_size

    @population_size.setter
    def population_size(self, value: int) -> None:
        self._population_size = value

    @property
    def crossover_pb(self) -> float:
        return self._crossover_pb

    @crossover_pb.setter
    def crossover_pb(self, value: float) -> None:
        self._crossover_pb = value

    @property
    def mutation_pb(self) -> float:
        return self._mutation_pb

    @mutation_pb.setter
    def mutation_pb(self, value: float) -> None:
        self._mutation_pb = value

    @property
    def max_gen(self) -> int:
        return self._max_gen

    @max_gen.setter
    def max_gen(self, value: int) -> None:
        self._max_gen = value