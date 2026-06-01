ACTION_NAMES = ["kick_left", "kick_right",
                "walk_front", "walk_back",
                "sidestep_left", "sidestep_right",
                "turn_left", "turn_right",
                "standup_back", "standup_front"]

RECORDING_DURATIONS = {
    "kick_left" : 2000,
    "kick_right" : 2000,
    "walk_front" : 4000,
    "walk_back" : 4000,
    "sidestep_left" : 4000,
    "sidestep_right" : 4000,
    "turn_left" : 4000,
    "turn_right" : 4000,
    "standup_back" : 8000,
    "standup_front" : 8000,
    "calculate_statistics" : 1000000
}

ROBOT_TELEPORTATION_INDEX = {
    "kick_left" : 2,
    "kick_right" : 2,
    "walk_front" : 2,
    "walk_back" : 2,
    "sidestep_left" : 2,
    "sidestep_right" : 2,
    "turn_left" : 2,
    "turn_right" : 2,
    "standup_back" : 0,
    "standup_front" : 1,
    "calculate_statistics" : -1
}

def get_train_data():
    actions = ACTION_NAMES
    date1 = "260528_0"
    date2 = "260529_0"
    actions_1 = [(action, date1, None) for action in actions]
    actions_2 = [(action, date2, None) for action in actions]
    return actions_1 + actions_2

def get_test_data():
    actions = ACTION_NAMES
    date1 = "260528_1"
    date2 = "260529_1"
    actions_1 = [(action, date1, None) for action in actions]
    actions_2 = [(action, date2, None) for action in actions]
    return actions_1 + actions_2

def get_combined_data():
    return get_train_data() + get_test_data()
