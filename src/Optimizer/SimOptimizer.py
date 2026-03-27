from typing import Optional
import numpy as np
import random
from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from ..Constants import JOINT_TYPES
from ..Simulator import Simulator
from ..Structs import Joint
from ..Utils import SimulationGapData, ExperimentMode, SimulationParameters

import logging
logger = logging.getLogger("global_logger")

def evaluate(experiments : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]],
             simulator : Simulator,
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
    gap_handler = simulator.simulation_gap(simulator_parameters, experiments, replay_mode=ExperimentMode.DEL_EXISTING)
    gap = gap_handler.get_final_FINAL_gap_avg(lambda gap_object: SimulationGapData.get_total_gap_avg(gap_object))
    # Return tuple (DEAP requirement)
    return (gap,)

class SimOptimizer:
    def __init__(self,
                 global_attributes : list[str],
                 per_joint_type_attributes : list[str],
                 experiments : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]] = None):
        """
        :param attribute_bounds: a dictionary containing the name of the attributes as keys and the lower and upper
        initialization bound as values
        :param experiments: which experiments should be used to evaluate individuals
        """
        self._global_attributes = global_attributes
        self._global_attribute_names = []
        self._per_joint_type_attributes = per_joint_type_attributes
        self._per_joint_type_attribute_names = []
        self._individual_dimension = len(global_attributes) + (5 * len(per_joint_type_attributes))
        self._experiments = experiments
        self._todoname = 0.1
        self._population_size = 20
        self._crossover_pb = 0.5
        self._mutation_pb = 0.2
        self._max_gen = 5
        self._simulator = Simulator()
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
            val = self._simulator.get_default_value(attribute_name)
            if type(val) is not float:
                logger.error("Global Parameter %s was not found", attribute_name)
            self._global_attribute_names.append(f"g_{attribute_name}")
            self._toolbox.register(f"g_{attribute_name}", random.uniform, val * (1 - self._todoname), val * (1 + self._todoname))
        #per-joint-type parameters
        for attribute_name in self._per_joint_type_attributes:
            for motor_index, joints_of_type in enumerate(JOINT_TYPES.values()):
                example_joint = joints_of_type[0]
                joint_object = self._simulator.get_default_value(example_joint)
                if type(joint_object) is not Joint:
                    logger.error("Per Joint Type %s was not found", attribute_name)
                attribute = getattr(joint_object, attribute_name, None)
                if attribute is None:
                    logger.error("Attribute for %s did not exists in %s", attribute_name, joint_object.__name__)
                self._per_joint_type_attribute_names.append(f"jt_{attribute_name}_{motor_index}")
                self._toolbox.register(f"jt_{attribute_name}_{motor_index}", random.uniform, attribute * (1 - self._todoname), attribute * (1 + self._todoname))
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
        # prefills 3 parameters, so only requires the individual
        self._toolbox.register("evaluate", evaluate, self._experiments, self._simulator, self._global_attribute_names, self._per_joint_type_attribute_names)

        # genetic operators to create new individuals
        self._toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self._toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=5.0, indpb=0.2)
        self._toolbox.register("select", tools.selTournament, tournsize=3)

    def run(self, seed : int = None):
        random.seed(seed)


        population = self._toolbox.population(n=self._population_size)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        halloffame = tools.HallOfFame(1)

        population, logbook = algorithms.eaSimple(
            population,
            self._toolbox,
            halloffame=halloffame,
            cxpb=self._crossover_pb,
            mutpb=self._mutation_pb,
            ngen=self._max_gen)
        return population, logbook
