from src import *
import matplotlib.pyplot as plt

def extraction_replay(test_object : SimulationGapData, joint_name : str, start_index : int, end_index : int, line_type : str):
    """
    Creates the following plots:

    1. shows the real robots position, velocity and acceleration

    2. shows the simulated robots position, velocity and acceleration
    """
    x_axis = test_object.get_time_steps(start_index, end_index)

    pos_extraction = test_object.get_pos_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    vel_extraction = test_object.get_vel_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    acc_extraction = test_object.get_acc_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)

    pos_replay = test_object.get_pos_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    vel_replay = test_object.get_vel_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    acc_replay = test_object.get_acc_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)

    plt.figure(figsize=(20, 5))
    plt.title("joint position, velocity and acceleration of the real robot")
    plt.xlabel("frame")
    plt.ylabel("position/velocity/acceleration")
    plt.plot(x_axis, pos_extraction[joint_name],line_type, color="yellow", label="pos")
    plt.plot(x_axis, vel_extraction[joint_name],line_type, color="green", label="vel")
    plt.plot(x_axis, acc_extraction[joint_name],line_type, color="blue", label="acc")
    plt.legend()
    plt.show()
    plt.figure(figsize=(20, 5))
    plt.title("joint position, velocity and acceleration of the simulated robot")
    plt.xlabel("frame")
    plt.ylabel("position/velocity/acceleration")
    plt.plot(x_axis, pos_replay[joint_name],line_type, color="yellow", label="pos")
    plt.plot(x_axis, vel_replay[joint_name],line_type, color="green", label="vel")
    plt.plot(x_axis, acc_replay[joint_name], line_type, color="blue", label="acc")
    plt.legend()
    plt.show()

def single_gap(test_object : SimulationGapData, joint_name : str, start_index : int, end_index : int, line_type : str):
    """
    Creates the following plots:

    1. position of the real and simulated robot and the resulting partial simulation gap

    2. velocity of the real and simulated robot and the resulting partial simulation gap

    3. acceleration of the real and simulated robot and the resulting partial simulation gap
    """

    x_axis = test_object.get_time_steps(start_index, end_index)

    pos_extraction = test_object.get_pos_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    pos_replay = test_object.get_pos_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    pos_gap = test_object.get_pos_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)

    vel_extraction = test_object.get_vel_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    vel_replay = test_object.get_vel_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    vel_gap = test_object.get_vel_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)

    acc_extraction = test_object.get_acc_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    acc_replay = test_object.get_acc_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    acc_gap = test_object.get_acc_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)

    plt.figure(figsize=(20, 5))
    plt.title("joint position of the real and simulated robot and the simulation gap between them.")
    plt.xlabel("frame")
    plt.ylabel("position/gap")
    plt.plot(x_axis, pos_extraction[joint_name],line_type, color="green", label="pos_real")
    plt.plot(x_axis, pos_replay[joint_name],line_type, color="red", label="pos_sim")
    plt.plot(x_axis, pos_gap[joint_name],line_type, color="blue", label="pos_gap")
    plt.legend()
    plt.show()

    plt.figure(figsize=(20, 5))
    plt.title("joint velocity of the real and simulated robot and the simulation gap between them.")
    plt.xlabel("frame")
    plt.ylabel("velocity/gap")
    plt.plot(x_axis, vel_extraction[joint_name],line_type, color="green", label="vel_real")
    plt.plot(x_axis, vel_replay[joint_name],line_type, color="red", label="vel_sim")
    plt.plot(x_axis, vel_gap[joint_name],line_type, color="blue", label="vel_gap")
    plt.legend()
    plt.show()

    plt.figure(figsize=(20, 5))
    plt.title("joint acceleration of the real and simulated robot and the simulation gap between them.")
    plt.xlabel("frame")
    plt.ylabel("acceleration/gap")
    plt.plot(x_axis, acc_extraction[joint_name],line_type, color="green", label="acc_real")
    plt.plot(x_axis, acc_replay[joint_name], line_type, color="red", label="acc_sim")
    plt.plot(x_axis, acc_gap[joint_name], line_type, color="blue", label="acc_gap")
    plt.legend()
    plt.show()

def total_gap(test_object : SimulationGapData, joint_name : str, start_index : int, end_index : int, line_type : str):
    """
    Creates the following plot:

    1. gap of the position, velocity, acceleration and their sum
    """
    x_axis = test_object.get_time_steps(start_index, end_index)

    pos_gap = test_object.get_pos_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    vel_gap = test_object.get_vel_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    acc_gap = test_object.get_acc_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)
    total_gap = test_object.get_total_gap(joint_names=[joint_name], start_index=start_index, end_index=end_index)

    plt.figure(figsize=(20, 5))
    plt.title("gap of the position, velocity, acceleration and their sum")
    plt.xlabel("frame")
    plt.ylabel("pos/vel/acc/total gap")
    plt.plot(x_axis, pos_gap[joint_name], line_type, color="yellow", label="pos_gap")
    plt.plot(x_axis, vel_gap[joint_name], line_type, color="blue", label="vel_gap")
    plt.plot(x_axis, acc_gap[joint_name], line_type, color="green", label="acc_gap")
    plt.plot(x_axis, total_gap[joint_name], line_type, color="red", label="total_gap")
    plt.legend()
    plt.show()

def avg_for_frames(test_object : SimulationGapData, start_index : int, end_index : int, line_type : str):
    """
    Creates the following plots:

    1. gap of the position, velocity, acceleration and their sum averaged over all joints
    """
    x_axis = test_object.get_time_steps(start_index, end_index)

    pos_gap = test_object.get_pos_gap_avg_for_frames(start_index=start_index, end_index=end_index)
    vel_gap = test_object.get_vel_gap_avg_for_frames(start_index=start_index, end_index=end_index)
    acc_gap = test_object.get_acc_gap_avg_for_frames(start_index=start_index, end_index=end_index)
    total_gap = test_object.get_total_gap_avg_for_frames(start_index=start_index, end_index=end_index)

    plt.figure(figsize=(20, 5))
    plt.title("gap of the position, velocity, acceleration and their sum averaged over all joints")
    plt.xlabel("frame")
    plt.ylabel("pos/vel/acc/total gap")
    plt.plot(x_axis, pos_gap, line_type, color="yellow", label="pos_gap")
    plt.plot(x_axis, vel_gap, line_type, color="blue", label="vel_gap")
    plt.plot(x_axis, acc_gap, line_type, color="green", label="acc_gap")
    plt.plot(x_axis, total_gap, line_type, color="red", label="total_gap")
    plt.legend()
    plt.show()

def avg_for_joints(test_object : SimulationGapData, line_type : str):
    """
    Creates the following plots:

    1. gap of the position, velocity, acceleration and their sum averaged over all frames
    """

    pos_gap = test_object.get_pos_gap_avg_for_joints()
    vel_gap = test_object.get_vel_gap_avg_for_joints()
    acc_gap = test_object.get_acc_gap_avg_for_joints()
    total_gap = test_object.get_total_gap_avg_for_joints()

    plt.figure(figsize=(20, 5))
    plt.title("gap of the position, velocity, acceleration and their sum averaged over all frames")
    plt.xlabel("joint")
    plt.ylabel("pos/vel/acc/total gap")
    plt.plot([JOINT_SHORT[joint_name] for joint_name in pos_gap.keys()], pos_gap.values(), line_type, color="yellow", label="pos_gap")
    plt.plot([JOINT_SHORT[joint_name] for joint_name in vel_gap.keys()], vel_gap.values(), line_type, color="green", label="vel_gap")
    plt.plot([JOINT_SHORT[joint_name] for joint_name in acc_gap.keys()], acc_gap.values(), line_type, color="blue", label="acc_gap")
    plt.plot([JOINT_SHORT[joint_name] for joint_name in total_gap.keys()], total_gap.values(), line_type, color="red", label="total_gap")
    plt.legend()
    plt.show()