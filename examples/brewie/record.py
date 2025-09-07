#!/usr/bin/env python

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
# from lerobot.record import record_loop  # Replaced with custom recording loop
from lerobot.robots.brewie.config_Brewie import BrewieConfig
from lerobot.robots.brewie.Brewie_base import BrewieBase
# from lerobot.teleoperators.keyboard import KeyboardTeleop, KeyboardTeleopConfig  # Removed - no teleop needed
from lerobot.utils.control_utils import init_keyboard_listener
# from lerobot.utils.utils import log_say  # Removed - using print instead
from lerobot.utils.visualization_utils import _init_rerun
import time

# Recording parameters
NUM_EPISODES = 3
FPS = 30
EPISODE_TIME_SEC = 30
RESET_TIME_SEC = 10
TASK_DESCRIPTION = "Brewie robot manipulation task"

def simple_record_loop(robot, dataset, control_time_s, fps, events):
    """Simple recording loop without teleoperators."""
    timestamp = 0
    start_episode_t = time.perf_counter()
    frame_interval = 1.0 / fps
    
    while timestamp < control_time_s and not events["stop_recording"]:
        start_loop_t = time.perf_counter()
        
        # Get observation from robot
        obs = robot.get_observation()
        
        # Create action (empty for passive recording)
        action = {key: 0.0 for key in robot.action_features.keys()}
        
        # Structure the frame correctly - flat structure
        frame = {}
        
        # Add observation data (motor positions and camera data)
        for key, value in obs.items():
            frame[key] = value
        
        # Add action data
        for key, value in action.items():
            frame[key] = value
        
        # Add to dataset
        dataset.add_frame(frame, timestamp)
        
        # Wait for next frame
        elapsed = time.perf_counter() - start_loop_t
        sleep_time = max(0, frame_interval - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        timestamp = time.perf_counter() - start_episode_t
        
        # Print progress every 5 seconds
        if int(timestamp) % 5 == 0 and timestamp > 0:
            print(f"Recording... {timestamp:.1f}s / {control_time_s}s")

# Create the robot configuration
robot_config = BrewieConfig(
    port="/dev/rrc",  # Adjust to your device path (COMx on Windows, /dev/ttyUSBx on Linux)
    id="brewie",
    use_degrees=True,  # Use degrees for joint positions
    max_relative_target=5,  # Safety limit: max 5 degrees per step
    cameras={},  # Add camera configs here if needed
)

# Initialize robot only (no teleoperator needed)
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

# Connect to robot only
robot.connect()

# _init_rerun(session_name="brewie_record")  # Disabled - Rerun viewer not required

listener, events = init_keyboard_listener()

if not robot.is_connected:
    raise ValueError("Robot is not connected!")

recorded_episodes = 0
while recorded_episodes < NUM_EPISODES and not events["stop_recording"]:
    print(f"Recording episode {recorded_episodes}")

    # Run the simple record loop
    simple_record_loop(
        robot=robot,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        fps=FPS,
        events=events
    )

    # Logic for reset env
    if not events["stop_recording"] and (
        (recorded_episodes < NUM_EPISODES - 1) or events["rerecord_episode"]
    ):
        print("Reset the environment")
        simple_record_loop(
            robot=robot,
            dataset=dataset,
            control_time_s=RESET_TIME_SEC,
            fps=FPS,
            events=events
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
