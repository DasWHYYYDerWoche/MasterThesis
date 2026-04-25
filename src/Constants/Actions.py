ACTION_NAMES = ["kick", "walk", "sidestep", "turn", "standup_back", "standup_front"]

RECORDING_DURATIONS = {
    "kick" : 1500,
    "walk" : 3000,
    "sidestep" : 3000,
    "turn" : 3000,
    "standup_back" : 6000,
    "standup_front" : 6000,
    "calculate_statistics" : 1000000
}

ROBOT_TELEPORTATION_IDENTIFIER = {
    "kick" : 2,
    "walk" : 2,
    "sidestep" : 2,
    "turn" : 2,
    "standup_back" : 0,
    "standup_front" : 1,
    "calculate_statistics" : -1
}