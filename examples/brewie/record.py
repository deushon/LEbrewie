#!/usr/bin/env python

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.record import record_loop
from lerobot.robots.brewie.config_Brewie import BrewieConfig
from lerobot.robots.brewie.Brewie_base import BrewieBase
from lerobot.teleoperators.keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.utils.control_utils import init_keyboard_listener
# from lerobot.utils.utils import log_say  # Removed - using print instead
from lerobot.utils.visualization_utils import _init_rerun

# Recording parameters
NUM_EPISODES = 3
FPS = 20
EPISODE_TIME_SEC = 10
RESET_TIME_SEC = 5
TASK_DESCRIPTION = "Brewie robot manipulation task"

# Create the robot configuration
robot_config = BrewieConfig(
    port="/dev/rrc",  # Adjust to your device path (COMx on Windows, /dev/ttyUSBx on Linux)
    id="brewie",
    use_degrees=True,  # Use degrees for joint positions
    max_relative_target=5,  # Safety limit: max 5 degrees per step
    cameras={},  # Add camera configs here if needed
)


# Initialize robot and teleoperator
robot = BrewieBase(robot_config)

# Configure the dataset features
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

# Create the dataset
dataset = LeRobotDataset.create(
    repo_id="forroot/brew_testx",  # Replace with your HuggingFace username and dataset name
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
)

# Connect to robot and teleoperator
robot.connect()

# _init_rerun(session_name="brewie_record")  # Disabled - Rerun viewer not required

listener, events = init_keyboard_listener()


recorded_episodes = 0
while recorded_episodes < NUM_EPISODES:
    print(f"Recording episode {recorded_episodes}")

    # Run the record loop
    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        dataset=dataset,
        teleop= None,
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=False,  # Disabled to avoid Rerun dependency
    )

    # Logic for reset env
    if not events["stop_recording"] and (
        (recorded_episodes < NUM_EPISODES - 1) or events["rerecord_episode"]
    ):
        print("Reset the environment")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop= None,
            control_time_s=RESET_TIME_SEC,
            single_task=TASK_DESCRIPTION,
            display_data=False,  # Disabled to avoid Rerun dependency
        )

    if events["rerecord_episode"]:
        print("Re-record episode")
        events["rerecord_episode"] = False
        events["exit_early"] = False
        dataset.clear_episode_buffer()
        continue

    dataset.save_episode()
    recorded_episodes += 1

# Upload to hub and clean up
dataset.push_to_hub()

robot.disconnect()
listener.stop()
