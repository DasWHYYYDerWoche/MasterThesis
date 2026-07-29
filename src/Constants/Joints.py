"""
Contains Information about the different joints, such as names, the used weights and shorthands.
"""



JOINT_NAMES = [
"lShoulderPitch","lShoulderRoll","lElbowYaw","lElbowRoll","lWristYaw",
"rShoulderPitch","rShoulderRoll","rElbowYaw","rElbowRoll","rWristYaw",
"lHipYawPitch","lHipRoll","lHipPitch","lKneePitch","lAnklePitch","lAnkleRoll",
"rHipYawPitch","rHipRoll","rHipPitch","rKneePitch","rAnklePitch","rAnkleRoll",
]

WEIGHTS = {
    # Head
    "headYaw": 0,
    "headPitch": 0,

    # Left Arm
    "lShoulderPitch": 1,
    "lShoulderRoll": 1,
    "lElbowYaw": 0.9,
    "lElbowRoll": 0.9,
    "lWristYaw": 0.8,
    "lHand" : 0,

    # Right Arm
    "rShoulderPitch": 1,
    "rShoulderRoll": 1,
    "rElbowYaw": 0.9,
    "rElbowRoll": 0.9,
    "rWristYaw": 0.8,
    "rHand" : 0,

    # Left Leg
    "lHipYawPitch": 1,
    "lHipRoll": 1,
    "lHipPitch": 1,
    "lKneePitch": 1.1,
    "lAnklePitch": 1,
    "lAnkleRoll": 1,

    # Right Leg
    "rHipYawPitch": 1,
    "rHipRoll": 1,
    "rHipPitch": 1,
    "rKneePitch": 1.1,
    "rAnklePitch": 1,
    "rAnkleRoll": 1,

    "x_gyro" : 1.25,
    "y_gyro" : 1.25,
    "z_gyro" : 1.25,
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
RANGES = {key : abs(value[0] - value[1]) for key, value in DEFLECTIONS.items()}

ABBREVIATIONS = {
    "combined":"Comb.",

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

    "x_gyro" : "xG",
    "y_gyro" : "yG",
    "z_gyro" : "zG",
}


#
JOINT_TYPES_5 = {
    0 : ["lHipYawPitch", "rHipYawPitch", "lHipRoll", "rHipRoll", "lAnkleRoll", "rAnkleRoll"],
    1 : ["lWristYaw", "rWristYaw"],
    2 : ["headYaw", "lElbowYaw", "rElbowYaw", "headPitch", "lShoulderRoll", "rShoulderRoll", "lElbowRoll", "rElbowRoll"],
    3 : ["lShoulderPitch", "rShoulderPitch"],
    4 : ["lHipPitch", "rHipPitch", "lKneePitch", "rKneePitch", "lAnklePitch", "rAnklePitch"]
}

"""
Somewhat dirty, some joints appear twice. The last appearance overwrites the any before, so
the shoulder rolls are part of motor type 2.5 and the value from motor type 2 gets overwritten.
"""
JOINT_TYPES_7 = {
    0 : ["lHipYawPitch", "rHipYawPitch", "lHipRoll", "rHipRoll", "lAnkleRoll", "rAnkleRoll"],
    1 : ["lWristYaw", "rWristYaw"],
    1.5 : [], #empty since the hands are unused
    2 : ["headYaw", "lElbowYaw", "rElbowYaw", "headPitch", "lShoulderRoll", "rShoulderRoll", "lElbowRoll", "rElbowRoll"],
    2.5 : ["headPitch", "lShoulderRoll", "rShoulderRoll", "lElbowRoll", "rElbowRoll"],
    3 : ["lShoulderPitch", "rShoulderPitch"],
    4 : ["lHipPitch", "rHipPitch", "lKneePitch", "rKneePitch", "lAnklePitch", "rAnklePitch"]
}

JOINT_GROUPS = {5 : JOINT_TYPES_5, 7 : JOINT_TYPES_7}

#unused, data is loaded from configuration file now
MAX_MOTOR_VELOCITY = {285.245901639344,1115.35269709544,1557.61589403974,469.954082651228,407.689643228265,500.698742263925,438.823079862438}