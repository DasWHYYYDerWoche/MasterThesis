class Experiment:
    def __init__(self, name : str, duration : int):
        self._name = name
        self._duration = duration

KICK : Experiment = Experiment("kick", 5)
WALK : Experiment = Experiment("walk",5)
TURN : Experiment = Experiment("turn",5)
SIDESTEP : Experiment = Experiment("sidestep",5)
STANDUP_FRONT : Experiment = Experiment("standup_front",5)
STANDUP_BACK : Experiment = Experiment("standup_back",5)