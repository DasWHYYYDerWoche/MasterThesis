class Hyperparameters:
    def __init__(self,
                 crossover_pb: float,
                 mutation_pb: float,
                 mutation_ind_pb: float,
                 tournament_size: float,
                 pop_size: int,
                 num_gen: int):
        self._crossover_pb: float = crossover_pb
        self._mutation_pb: float = mutation_pb
        self._mutation_ind_pb: float = mutation_ind_pb
        self._tournament_size: float = tournament_size
        self._pop_size: int = pop_size
        self._num_gen: int = num_gen

    def __str__(self):
        return (
            f"crossover_pb = {self._crossover_pb}\n"
            f"mutation_pb = {self._mutation_pb}\n"
            f"mutation_ind_pb = {self._mutation_ind_pb}\n"
            f"sel_tournament_size = {self._tournament_size}\n"
            f"pop_size = {self._pop_size}\n"
            f"num_gen = {self._num_gen}"
        )

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
    def mutation_sigma(self) -> float:
        return self._mutation_sigma

    @mutation_sigma.setter
    def mutation_sigma(self, value: float) -> None:
        self._mutation_sigma = value

    @property
    def mutation_ind_pb(self) -> float:
        return self._mutation_ind_pb

    @mutation_ind_pb.setter
    def mutation_ind_pb(self, value: float) -> None:
        self._mutation_ind_pb = value

    @property
    def tournament_size(self) -> float:
        return self._tournament_size

    @tournament_size.setter
    def tournament_size(self, value: float) -> None:
        self._tournament_size = value

    @property
    def init_offset_factor(self) -> float:
        return self._init_offset_factor

    @init_offset_factor.setter
    def init_offset_factor(self, value: float) -> None:
        self._init_offset_factor = value

    @property
    def lower_bound_factor(self) -> float:
        return self._lower_bound_factor

    @lower_bound_factor.setter
    def lower_bound_factor(self, value: float) -> None:
        self._lower_bound_factor = value

    @property
    def upper_bound_factor(self) -> float:
        return self._upper_bound_factor

    @upper_bound_factor.setter
    def upper_bound_factor(self, value: float) -> None:
        self._upper_bound_factor = value

    @property
    def pop_size(self) -> int:
        return self._pop_size

    @pop_size.setter
    def pop_size(self, value: int) -> None:
        self._pop_size = value

    @property
    def num_gen(self) -> int:
        return self._num_gen

    @num_gen.setter
    def num_gen(self, value: int) -> None:
        self._num_gen = value