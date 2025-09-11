#!/usr/bin/env python3

"""
Tests for Brewie robot ROS integration.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from lerobot.robots.brewie import BrewieBase, BrewieConfig


class TestBrewieROS:
    
    def setup_method(self):
        """Setup test configuration."""
        self.config = BrewieConfig(
            master_ip="localhost",
            master_port=9090,
            servo_duration=0.1,
            max_relative_target=None,
            disable_torque_on_disconnect=True
        )
    
    @patch('roslibpy.Ros')
    def test_robot_initialization(self, mock_ros):
        """Test robot initialization."""
        robot = BrewieBase(self.config)
        
        assert robot.config == self.config
        assert robot.ros_client is None
        assert robot.latest_image is None
        assert len(robot.current_positions) == 0
        assert robot.joint_to_id == {v: k for k, v in self.config.servo_mapping.items()}
    
    @patch('roslibpy.Ros')
    def test_connection(self, mock_ros_class):
        """Test ROS connection."""
        mock_ros = Mock()
        mock_ros.is_connected = True
        mock_ros_class.return_value = mock_ros
        
        robot = BrewieBase(self.config)
        
        with patch.object(robot, '_setup_ros_services'), \
             patch.object(robot, '_setup_ros_topics'):
            robot.connect()
        
        assert robot.ros_client == mock_ros
        mock_ros.run.assert_called_once()
    
    @patch('roslibpy.Ros')
    def test_observation_features(self, mock_ros):
        """Test observation features."""
        robot = BrewieBase(self.config)
        
        features = robot.observation_features
        
        # Check that all joints are included
        expected_joints = list(self.config.servo_mapping.values())
        for joint in expected_joints:
            assert f"{joint}.pos" in features
        
        # Check camera feature
        assert "camera" in features
    
    @patch('roslibpy.Ros')
    def test_action_features(self, mock_ros):
        """Test action features."""
        robot = BrewieBase(self.config)
        
        features = robot.action_features
        
        # Check that all joints are included
        expected_joints = list(self.config.servo_mapping.values())
        for joint in expected_joints:
            assert f"{joint}.pos" in features
    
    @patch('roslibpy.Ros')
    def test_get_observation_with_ros_service(self, mock_ros_class):
        """Test getting observation via ROS service."""
        mock_ros = Mock()
        mock_ros.is_connected = True
        mock_ros_class.return_value = mock_ros
        
        robot = BrewieBase(self.config)
        robot.ros_client = mock_ros
        
        # Mock position service
        mock_service = Mock()
        mock_service.call.return_value = {
            'success': True,
            'position': [
                {'id': 13, 'position': 500},
                {'id': 14, 'position': 600},
                {'id': 15, 'position': 700}
            ]
        }
        robot.position_service = mock_service
        
        # Mock camera
        robot.latest_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        obs = robot.get_observation()
        
        # Check servo positions
        assert "left_shoulder_pan.pos" in obs
        assert obs["left_shoulder_pan.pos"] == 500
        assert "right_shoulder_pan.pos" in obs
        assert obs["right_shoulder_pan.pos"] == 600
        assert "left_shoulder_lift.pos" in obs
        assert obs["left_shoulder_lift.pos"] == 700
        
        # Check camera
        assert "camera" in obs
        assert obs["camera"].shape == (480, 640, 3)
    
    @patch('roslibpy.Ros')
    def test_send_action(self, mock_ros_class):
        """Test sending action via ROS topic."""
        mock_ros = Mock()
        mock_ros.is_connected = True
        mock_ros_class.return_value = mock_ros
        
        robot = BrewieBase(self.config)
        robot.ros_client = mock_ros
        
        # Mock set position topic
        mock_topic = Mock()
        robot.set_position_topic = mock_topic
        
        # Mock current positions
        robot.current_positions = {
            "left_shoulder_pan.pos": 500,
            "right_shoulder_pan.pos": 500
        }
        
        action = {
            "left_shoulder_pan.pos": 600,
            "right_shoulder_pan.pos": 700
        }
        
        result = robot.send_action(action)
        
        # Check that topic was called
        mock_topic.publish.assert_called_once()
        
        # Check returned action
        assert result["left_shoulder_pan.pos"] == 600
        assert result["right_shoulder_pan.pos"] == 700
    
    @patch('roslibpy.Ros')
    def test_disconnect(self, mock_ros_class):
        """Test disconnection."""
        mock_ros = Mock()
        mock_ros.is_connected = True
        mock_ros_class.return_value = mock_ros
        
        robot = BrewieBase(self.config)
        robot.ros_client = mock_ros
        
        robot.disconnect()
        
        mock_ros.close.assert_called_once()
        assert robot.ros_client is None


if __name__ == "__main__":
    pytest.main([__file__])
