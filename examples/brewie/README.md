# Brewie Robot Recording Example

This example shows how to record datasets with the Brewie robot using LeRobot.

## Setup

1. **Hardware Connection**: Connect your Hiwonder controller board to the computer via USB. The default device path is `/dev/rrc` on Linux or `COMx` on Windows.

2. **Servo Configuration**: The script is configured for the following servo IDs:
   - Left gripper: 21
   - Right gripper: 22
   - Left forearm pitch: 19
   - Right forearm pitch: 20
   - Left forearm roll: 17
   - Right forearm roll: 18
   - Left shoulder lift: 15
   - Right shoulder lift: 16
   - Left shoulder pan: 13
   - Right shoulder pan: 14

3. **Camera Setup** (Optional): Add camera configurations to the `robot_config.cameras` dictionary if you want to record video data.

## Usage

1. **Configure the script**:
   - Update `robot_config.port` to match your device path
   - Set your HuggingFace username and dataset name in `dataset.repo_id`
   - Adjust recording parameters (episodes, duration, FPS) as needed

2. **Run the recording**:
   ```bash
   python examples/brewie/record.py
   ```

3. **Controls**:
   - Use keyboard teleoperation to control the robot
   - Follow the on-screen prompts for recording episodes
   - The dataset will be automatically uploaded to HuggingFace Hub

## Configuration Options

- `use_degrees=True`: Use degrees for joint positions (recommended)
- `max_relative_target=5`: Safety limit for joint movements (5 degrees per step)
- `FPS=30`: Recording frame rate
- `EPISODE_TIME_SEC=30`: Duration of each episode
- `NUM_EPISODES=3`: Number of episodes to record

## Troubleshooting

- **Connection issues**: Check that the device path is correct and the controller is connected
- **Servo not responding**: Verify servo IDs match your hardware configuration
- **Permission errors**: On Linux, you may need to add your user to the dialout group: `sudo usermod -a -G dialout $USER`
