ACTION_NAMES = ["kick", "walk", "sidestep", "turn", "standup_back", "standup_front"]

RECORDING_DURATIONS = {
    "kick" : 2000,
    "walk" : 4000,
    "sidestep" : 4000,
    "turn" : 4000,
    "standup_back" : 8000,
    "standup_front" : 8000,
    "calculate_statistics" : 1000000
}

ROBOT_TELEPORTATION_INDEX = {
    "kick" : 2,
    "walk" : 2,
    "sidestep" : 2,
    "turn" : 2,
    "standup_back" : 0,
    "standup_front" : 1,
    "calculate_statistics" : -1
}