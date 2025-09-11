#!/usr/bin/env python3

"""
Example script for using Brewie robot with ROS integration.
This script demonstrates how to connect to the robot via ROS and perform basic operations.
"""

import time
import logging
from lerobot.robots.brewie import BrewieBase, BrewieConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Create configuration for ROS-based Brewie robot
    config = BrewieConfig(
        master_ip="192.168.20.21",  # Change to your ROS master IP
        master_port=9090,       # Change to your ROS master port
        servo_duration=0.1,     # Duration for servo movements
        max_relative_target=50,  # Maximum relative movement per step (for safety)
        disable_torque_on_disconnect=True
    )
    
    # Create robot instance
    robot = BrewieBase(config)
    
    try:
        # Connect to robot
        logger.info("Connecting to robot...")
        robot.connect()
        
        # Get initial observation
        logger.info("Getting initial observation...")
        obs = robot.get_observation()
        logger.info(f"Initial positions: {obs}")
        
        # Example: Move all joints slightly
        logger.info("Sending test action...")
        test_action = {}
        for joint_name in config.servo_mapping.values():
            # Get current position and add small offset
            current_pos = obs.get(f"{joint_name}.pos", 500)  # Default to middle position
            new_pos = current_pos + 50  # Move 50 units
            test_action[f"{joint_name}.pos"] = new_pos
        
        robot.send_action(test_action)
        
        # Wait a bit for movement
        time.sleep(1.0)
        
        # Get observation after movement
        logger.info("Getting observation after movement...")
        obs_after = robot.get_observation()
        logger.info(f"Positions after movement: {obs_after}")
        
        # Example: Return to initial positions
        logger.info("Returning to initial positions...")
        robot.send_action(obs)  # Use initial observation as action
        
        time.sleep(1.0)
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        logger.error("Possible causes:")
        logger.error("1. ROS master is not running at the specified IP/port")
        logger.error("2. ROS service '/ros_robot_controller/bus_servo/get_position' is not available")
        logger.error("3. Robot controller is not running")
        logger.error("4. Network connectivity issues")
        
    finally:
        # Disconnect
        if robot.is_connected:
            logger.info("Disconnecting from robot...")
            robot.disconnect()

if __name__ == "__main__":
    main()
