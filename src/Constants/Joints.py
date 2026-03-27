NAMES = [
"headYaw","headPitch",
"lShoulderPitch","lShoulderRoll","lElbowYaw","lElbowRoll","lWristYaw",
"rShoulderPitch","rShoulderRoll","rElbowYaw","rElbowRoll","rWristYaw",
"lHipYawPitch","lHipRoll","lHipPitch","lKneePitch","lAnklePitch","lAnkleRoll",
"rHipYawPitch","rHipRoll","rHipPitch","rKneePitch","rAnklePitch","rAnkleRoll",
]

WEIGHTS = {
    # Head
    "headYaw": 1,
    "headPitch": 1,

    # Left Arm
    "lShoulderPitch": 1,
    "lShoulderRoll": 1,
    "lElbowYaw": 1,
    "lElbowRoll": 1,
    "lWristYaw": 1,
    "lHand" : 1,

    # Right Arm
    "rShoulderPitch": 1,
    "rShoulderRoll": 1,
    "rElbowYaw": 1,
    "rElbowRoll": 1,
    "rWristYaw": 1,
    "rHand" : 1,

    # Left Leg
    "lHipYawPitch": 1,
    "lHipRoll": 1,
    "lHipPitch": 1,
    "lKneePitch": 1,
    "lAnklePitch": 1,
    "lAnkleRoll": 1,

    # Right Leg
    "rHipYawPitch": 1,
    "rHipRoll": 1,
    "rHipPitch": 1,
    "rKneePitch": 1,
    "rAnklePitch": 1,
    "rAnkleRoll": 1,
}

DEFLECTIONS = {
    # Head
    "headYaw": (-119.5, 119.5),
    "headPitch": (-38.5, 29.5),

    # Left Arm
    "lShoulderPitch": (-119.5, 119.5),
    "lShoulderRoll": (-18.0, 76.0),
    "lElbowYaw": (-119.5, 119.5),
    "lElbowRoll": (-88.5, -2.0),
    "lWristYaw": (-104.5, 104.5),
    "lHand" : (0,1),

    # Right Arm
    "rShoulderPitch": (-119.5, 119.5),
    "rShoulderRoll": (-76.0, 18.0),
    "rElbowYaw": (-119.5, 119.5),
    "rElbowRoll": (2.0, 88.5),
    "rWristYaw": (-104.5, 104.5),
    "rHand" : (0,1),

    # Left Leg
    "lHipYawPitch": (-65.62, 42.44),
    "lHipRoll": (-21.74, 45.29),
    "lHipPitch": (-88.0, 27.73),
    "lKneePitch": (-5.29, 121.04),
    "lAnklePitch": (-68.15, 52.86),
    "lAnkleRoll": (-22.79, 44.06),

    # Right Leg
    "rHipYawPitch": (-65.62, 42.44),
    "rHipRoll": (-45.29, 21.74),
    "rHipPitch": (-88.0, 27.73),
    "rKneePitch": (-5.90, 121.47),
    "rAnklePitch": (-67.97, 53.40),
    "rAnkleRoll": (-44.06, 22.80),
}

ABBREVIATIONS = {
    "headYaw": "HY",
    "headPitch": "HP",

    "lShoulderPitch": "LSP",
    "lShoulderRoll": "LSR",
    "lElbowYaw": "LEY",
    "lElbowRoll": "LER",
    "lWristYaw": "LWY",

    "rShoulderPitch": "RSP",
    "rShoulderRoll": "RSR",
    "rElbowYaw": "REY",
    "rElbowRoll": "RER",
    "rWristYaw": "RWY",

    "lHipYawPitch": "LHipYP",
    "lHipRoll": "LHipR",
    "lHipPitch": "LHipP",
    "lKneePitch": "LKP",
    "lAnklePitch": "LAP",
    "lAnkleRoll": "LAR",

    "rHipYawPitch": "RHipYP",
    "rHipRoll": "RHipR",
    "rHipPitch": "RHipP",
    "rKneePitch": "RKP",
    "rAnklePitch": "RAP",
    "rAnkleRoll": "RAR",
}

JOINT_TYPES = {
    0 : ["lHipYawPitch", "rHipYawPitch", "lHipRoll", "rHipRoll", "lAnkleRoll", "rAnkleRoll"],
    1 : ["lWristYaw", "rWristYaw", "lHand", "rHand"],
    2 : ["headYaw", "lElbowYaw", "rElbowYaw", "headPitch", "lShoulderRoll", "rShoulderRoll", "lElbowRoll", "rElbowRoll"],
    3 : ["lShoulderPitch", "rShoulderPitch"],
    4 : ["lHipPitch", "rHipPitch", "lKneePitch", "rKneePitch", "lAnklePitch", "rAnklePitch"]
}

RANGES = {key : abs(value[0] - value[1]) for key, value in DEFLECTIONS.items()}