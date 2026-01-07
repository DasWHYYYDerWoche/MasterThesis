import pathlib

# -------- paths --------

REPO_PATH : pathlib.Path = pathlib.Path.home() / "source" / "repos" / "NDevils2015"
#path to the config of the jointRequestProvider
JRP_PATH : pathlib.Path = REPO_PATH / "Config" / "jointRequestProvider.cfg"
#path to logs containing JSD and JS from the log recorded on the field
LOGS_FIELD_PATH : pathlib.Path = REPO_PATH / "Config" / "Logs" / "CSVLogger" / "recording"
#path to the logs of the replay in the simulation
LOGS_REPLAY_PATH : pathlib.Path = REPO_PATH / "Config" / "Logs" / "CSVLogger" / "loading"

# -------- experiment file names --------

KICK : str = "kick"
WALK : str = "walk"
SIDESTEP : str = "sidestep"
STANDUP_FRONT : str = "standup_front"
STANDUP_BACK : str = "standup_back"


def update_cfg(path : pathlib.Path, replacement : list[tuple[str, str]]) -> bool:
    file_text = ""
    with open(path, "r") as f:
        file_text = f.read()
    #change text
    for (old, new) in replacement:
        file_text = file_text.replace(old, new)
    with open(path, "w") as f:
        f.write(file_text)
    return True