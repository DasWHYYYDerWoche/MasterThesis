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
from ..Simulator import Simulator
from ..Structs import Joint
from ..Utils import SimulationGapHandler, SimulationGapData, ExperimentMode, SimulationParameters, ExperimentParameters

import logging
logger = logging.getLogger("global_logger")


class SimOptimizer:
    def __init__(self,
                 global_attributes : list[str],
                 per_joint_type_attributes : list[str],
                 experiments : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]] = None,
                 population_size : int = 20,
                 max_gen : int = 100,
                 crossover_pb : float = 0.5,
                 mutation_pb : float = 0.2):
        """
        :param attribute_bounds: a dictionary containing the name of the attributes as keys and the lower and upper
        initialization bound as values
        :param experiments: which experiments should be used to evaluate individuals
        """
        self._global_attributes = global_attributes
        self._global_attribute_names = []
        self._global_attribute_boundaries = []
        self._per_joint_type_attributes = per_joint_type_attributes
        self._per_joint_type_attribute_names = []
        self._per_joint_type_attribute_boundaries = []
        self._individual_dimension = len(global_attributes) + (5 * len(per_joint_type_attributes))
        self._experiments = experiments

        self._initialization_offset = 0.1
        self._lower_bound_factor = 0.001
        self._upper_bound_factor = 100

        self._population_size = population_size
        self._crossover_pb = crossover_pb
        self._mutation_pb = mutation_pb
        self._max_gen = max_gen

        self._simulator = Simulator()
        self._simulator.batch_size = 5

        settings = SimulationParameters("default")
        default_gap_handler = self._simulator.simulation_gap(settings)
        self._pos_scale_factor, self._vel_scale_factor, self._acc_scale_factor = default_gap_handler.get_scale_factors()
        print([self._pos_scale_factor, self._vel_scale_factor, self._acc_scale_factor])
        default_gap_handler.unload()

        self._toolbox = base.Toolbox()
        self._create_classes()
        self._init_toolbox()




    def _create_classes(self):
        # create classes given a name, a baseclass and arguments given to the class during creation
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        

    def _init_toolbox(self):
        # creates a method attr_name for each attribute that samples a random value from their within its boundaries
        #global parameters
        for attribute_name in self._global_attributes:
            print(attribute_name)
            value = self._simulator.get_default_value(attribute_name)
            if type(value) is None:
                print(attribute_name)
                print(value)
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
                               self._experiments, self._simulator, self._global_attribute_names, self._per_joint_type_attribute_names,
                               self._pos_scale_factor, self._vel_scale_factor, self._acc_scale_factor)

        def mate(individual1, individual2):
            i1, i2 = tools.cxBlend(individual1, individual2, alpha = 0.5)
            SimOptimizer.clamp(i1, self._global_attribute_boundaries + self._per_joint_type_attribute_boundaries)
            SimOptimizer.clamp(i2, self._global_attribute_boundaries + self._per_joint_type_attribute_boundaries)
            return i1,i2

        def mutate(individual):
            tools.mutGaussian(individual, mu=0, sigma=5.0, indpb=0.2),
            SimOptimizer.clamp(individual, self._global_attribute_boundaries + self._per_joint_type_attribute_boundaries)
            return (individual,)

        # genetic operators to create new individuals
        self._toolbox.register("mate", mate)
        self._toolbox.register("mutate", mutate)
        self._toolbox.register("select", tools.selTournament, tournsize=3)

    def run(self, seed : int = None):
        current_time_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        directory = Path("run_" + current_time_str)
        self._create_log_file(directory)

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
        df = pd.DataFrame(logbook)
        df.to_csv(directory / "logbook", index=False)
        df = pd.DataFrame(halloffame)
        df.columns = self._global_attribute_names + self._per_joint_type_attribute_names
        df.to_csv(directory / "hallOfFame", index=False)

        return population, logbook, stats

    def _create_log_file(self, directory : Path):
        full_path = os.getcwd() / directory / "Hyperparameters.txt"
        full_path.parent.mkdir(parents=True)
        text = ""
        text += "population_size =" + str(self._population_size) + "\n"
        text += "crossover_pb =" + str(self._crossover_pb) + "\n"
        text += "mutation_pb =" + str(self._mutation_pb) + "\n"
        text += "generations =" + str(self._max_gen) + "\n"
        text += "initialization_offset =" + str(self._initialization_offset) + "\n"
        f = None
        try:
            f = open(full_path, "w")
            f.write(text)
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    # -------- static methods --------

    @staticmethod
    def evaluate(experiments: Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]],
                 simulator: Simulator,
                 global_attribute_names: list[str],
                 per_joint_type_attribute_names: list[str],
                 pos_scale_factor : float,
                 vel_scale_factor : float,
                 acc_scale_factor : float,
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
        gap_handler.set_scale_factors(pos_scale_factor, vel_scale_factor, acc_scale_factor)
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