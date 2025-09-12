#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import time
import threading
from functools import cached_property
from typing import Any
import numpy as np
import cv2
from io import BytesIO

import roslibpy
from roslibpy import Ros, Service, ServiceRequest, Topic, Message

from lerobot.cameras.utils import make_cameras_from_configs
from lerobot.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..robot import Robot
from ..utils import ensure_safe_goal_position
from .config_Brewie import BrewieConfig

logger = logging.getLogger(__name__)


class BrewieBase(Robot):

    config_class = BrewieConfig
    name = "BrewieBase"

    def __init__(self, config: BrewieConfig):
        super().__init__(config)
        self.config = config
        
        # ROS connection
        self.ros_client = None
        self.position_service = None
        self.set_position_topic = None
        self.camera_topic = None
        
        # Camera data
        self.latest_image = None
        self.image_lock = threading.Lock()
        
        # Servo positions cache
        self.current_positions = {}
        self.position_lock = threading.Lock()
        
        # Create reverse mapping (joint_name -> servo_id)
        self.joint_to_id = {v: k for k, v in config.servo_mapping.items()}
        
        # Initialize cameras if configured
        self.cameras = make_cameras_from_configs(config.cameras) if config.cameras else {}

    @property
    def _motors_ft(self) -> dict[str, type]:
        # Return features for all joints defined in servo_mapping
        return {f"{joint}.pos": int for joint in self.config.servo_mapping.values()}

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        if self.cameras:
            return {
                cam: (self.config.cameras[cam].height, self.config.cameras[cam].width, 3) for cam in self.cameras
            }
        else:
            # Default camera dimensions for ROS camera
            return {"camera": (480, 640, 3)}

    @cached_property
    def observation_features(self) -> dict[str, type | tuple]:
        return {**self._motors_ft, **self._cameras_ft}

    @cached_property
    def action_features(self) -> dict[str, type]:
        return self._motors_ft

    @property
    def is_connected(self) -> bool:
        ros_connected = self.ros_client is not None and self.ros_client.is_connected
        cameras_connected = all(cam.is_connected for cam in self.cameras.values()) if self.cameras else True
        return ros_connected and cameras_connected

    def connect(self, calibrate: bool = True) -> None:
        """
        Connect to ROS and initialize services and topics.
        """
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} already connected")

        # Connect to ROS
        self.ros_client = Ros(host=self.config.master_ip, port=self.config.master_port)
        self.ros_client.run()
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        while not self.ros_client.is_connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if not self.ros_client.is_connected:
            raise ConnectionError(f"Failed to connect to ROS at {self.config.master_ip}:{self.config.master_port}")
        
        # Initialize services and topics
        self._setup_ros_services()
        self._setup_ros_topics()
        
        # Connect cameras if configured
        for cam in self.cameras.values():
            cam.connect()
        
        logger.info(f"{self} connected to ROS at {self.config.master_ip}:{self.config.master_port}")

    def _setup_ros_services(self):
        """Setup ROS services for servo control."""
        self.position_service = Service(
            self.ros_client, 
            self.config.position_service, 
            'ros_robot_controller/GetBusServosPosition'
        )

    def _setup_ros_topics(self):
        """Setup ROS topics for servo control and camera."""
        self.set_position_topic = Topic(
            self.ros_client,
            self.config.set_position_topic,
            'ros_robot_controller/SetBusServosPosition'
        )
        
        # Setup camera topic if not using standard cameras
        if not self.cameras:
            self.camera_topic = Topic(
                self.ros_client,
                self.config.camera_topic,
                'sensor_msgs/CompressedImage'
            )
            self.camera_topic.subscribe(self._camera_callback)

    def _camera_callback(self, message):
        """Callback for ROS camera topic."""
        try:
            # Decode compressed image
            img_data = message['data']
            # Handle both string and bytes data
            if isinstance(img_data, str):
                # Convert string to bytes if needed
                img_data = img_data.encode('latin-1')
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                with self.image_lock:
                    self.latest_image = img
        except Exception as e:
            logger.error(f"Error processing camera image: {e}")

    @property
    def is_calibrated(self) -> bool:
        # For ROS-based control, we assume the robot is always "calibrated"
        # since calibration is handled by the ROS controller
        return True

    def calibrate(self) -> None:
        """
        For ROS-based control, calibration is handled by the ROS controller.
        This method is kept for compatibility but does nothing.
        """
        logger.info("Calibration is handled by the ROS controller. Skipping local calibration.")

    def configure(self) -> None:
        """
        For ROS-based control, configuration is handled by the ROS controller.
        This method is kept for compatibility but does nothing.
        """
        logger.info("Configuration is handled by the ROS controller. Skipping local configuration.")

    def setup_motors(self) -> None:
        """
        For ROS-based control, motor setup is handled by the ROS controller.
        This method is kept for compatibility but does nothing.
        """
        logger.info("Motor setup is handled by the ROS controller. Skipping local setup.")

    def get_observation(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        obs_dict = {}
        
        # Read servo positions via ROS service
        start = time.perf_counter()
        try:
            request = ServiceRequest({'id': self.config.servo_ids})
            result = self.position_service.call(request)
            
            if result.get('success', False):
                positions = result.get('position', [])
                for pos_data in positions:
                    servo_id = pos_data['id']
                    position = pos_data['position']
                    joint_name = self.config.servo_mapping.get(servo_id)
                    if joint_name:
                        # Ensure position is integer and within valid range (0-1000)
                        position = max(0, min(1000, int(position)))
                        obs_dict[f"{joint_name}.pos"] = position
                        
                with self.position_lock:
                    self.current_positions = obs_dict.copy()
            else:
                logger.warning("Failed to get servo positions from ROS service")
                
        except Exception as e:
            logger.error(f"Error reading servo positions: {e}")
            # Use cached positions if available
            with self.position_lock:
                obs_dict = self.current_positions.copy()
        
        dt_ms = (time.perf_counter() - start) * 1e3
        logger.debug(f"{self} read servo state: {dt_ms:.1f}ms")

        # Get camera data
        if self.cameras:
            # Use standard cameras
            for cam_key, cam in self.cameras.items():
                start = time.perf_counter()
                obs_dict[cam_key] = cam.async_read()
                dt_ms = (time.perf_counter() - start) * 1e3
                logger.debug(f"{self} read {cam_key}: {dt_ms:.1f}ms")
        else:
            # Use ROS camera
            with self.image_lock:
                if self.latest_image is not None:
                    obs_dict["camera"] = self.latest_image.copy()
                else:
                    # Return empty image if no data available
                    obs_dict["camera"] = np.zeros((480, 640, 3), dtype=np.uint8)

        return obs_dict

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Command arm to move to a target joint configuration via ROS.

        The relative action magnitude may be clipped depending on the configuration parameter
        `max_relative_target`. In this case, the action sent differs from original action.
        Thus, this function always returns the action actually sent.

        Raises:
            RobotDeviceNotConnectedError: if robot is not connected.

        Returns:
            the action sent to the servos, potentially clipped.
        """
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        goal_pos = {key.removesuffix(".pos"): val for key, val in action.items() if key.endswith(".pos")}

        # Cap goal position when too far away from present position.
        if self.config.max_relative_target is not None:
            with self.position_lock:
                present_pos = {key.removesuffix(".pos"): val for key, val in self.current_positions.items()}
            goal_present_pos = {key: (g_pos, present_pos.get(key, 0)) for key, g_pos in goal_pos.items()}
            # Convert max_relative_target to float if it's not None
            max_relative = float(self.config.max_relative_target)
            goal_pos = ensure_safe_goal_position(goal_present_pos, max_relative)

        # Convert joint positions to servo positions and send via ROS
        try:
            new_positions = []
            for joint_name, position in goal_pos.items():
                servo_id = self.joint_to_id.get(joint_name)
                if servo_id is not None:
                    # Ensure position is within valid range (0-1000)
                    position = max(0, min(1000, int(position)))
                    new_positions.append({'id': servo_id, 'position': position})
            
            if new_positions:
                servo_msg = Message({
                    'duration': self.config.servo_duration,
                    'position': new_positions,
                })
                self.set_position_topic.publish(servo_msg)
                
        except Exception as e:
            logger.error(f"Error sending servo positions: {e}")

        return {f"{joint}.pos": val for joint, val in goal_pos.items()}

    def disconnect(self):
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        # Disconnect cameras
        for cam in self.cameras.values():
            cam.disconnect()
        
        # Disconnect ROS
        if self.ros_client and self.ros_client.is_connected:
            self.ros_client.close()
            self.ros_client = None

        logger.info(f"{self} disconnected from ROS.")
