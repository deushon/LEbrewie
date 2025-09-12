#!/usr/bin/env python3

"""
Тестовый скрипт для проверки улучшенной обработки изображений в Brewie.
Этот скрипт демонстрирует новую функциональность CameraSubscriber.
"""

import time
import logging
import cv2
import numpy as np
from lerobot.robots.brewie import BrewieBase, BrewieConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_camera_processing():
    """Тестирует улучшенную обработку изображений."""
    
    # Create configuration for ROS-based Brewie robot
    config = BrewieConfig(
        master_ip="192.168.20.21",  # Change to your ROS master IP
        master_port=9090,           # Change to your ROS master port
        servo_duration=0.1,         # Duration for servo movements
        max_relative_target=50,     # Maximum relative movement per step (for safety)
        disable_torque_on_disconnect=True
    )
    
    # Create robot instance
    robot = BrewieBase(config)
    
    try:
        # Connect to robot
        logger.info("Connecting to robot...")
        robot.connect()
        
        # Test camera connection
        logger.info("Testing camera connection...")
        camera_test_result = robot.test_camera_connection()
        logger.info(f"Camera test result: {camera_test_result}")
        
        if not camera_test_result["camera_available"]:
            logger.error("Camera is not available. Check ROS camera topic.")
            return
        
        # Test image processing for several iterations
        logger.info("Testing image processing...")
        for i in range(5):
            logger.info(f"--- Test iteration {i+1} ---")
            
            # Get observation (includes camera data)
            obs = robot.get_observation()
            
            # Check if camera data is present
            if "camera" in obs:
                camera_data = obs["camera"]
                if isinstance(camera_data, np.ndarray) and camera_data.size > 0:
                    logger.info(f"✓ Camera data received: shape={camera_data.shape}, dtype={camera_data.dtype}")
                    
                    # Test image properties
                    if len(camera_data.shape) == 3:
                        height, width, channels = camera_data.shape
                        logger.info(f"✓ Image dimensions: {width}x{height}x{channels}")
                        
                        # Check if image is not empty (all zeros)
                        if np.any(camera_data):
                            logger.info("✓ Image contains non-zero data")
                        else:
                            logger.warning("⚠ Image is empty (all zeros)")
                    else:
                        logger.warning(f"⚠ Unexpected image shape: {camera_data.shape}")
                else:
                    logger.warning("⚠ Camera data is empty or invalid")
            else:
                logger.warning("⚠ No camera data in observation")
            
            # Wait between tests
            time.sleep(1.0)
        
        logger.info("Camera processing test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during camera test: {e}")
        logger.error("Possible causes:")
        logger.error("1. ROS master is not running at the specified IP/port")
        logger.error("2. ROS camera topic is not publishing data")
        logger.error("3. Camera topic format is not 'sensor_msgs/CompressedImage'")
        logger.error("4. Network connectivity issues")
        
    finally:
        # Disconnect
        if robot.is_connected:
            logger.info("Disconnecting from robot...")
            robot.disconnect()

def test_image_decoding():
    """Тестирует декодирование изображений с различными форматами."""
    
    logger.info("Testing image decoding with different formats...")
    
    # Test with sample Base64 data (small test image)
    test_base64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A"
    
    # Create a mock message
    mock_message = {"data": test_base64}
    
    # Test the decoding function
    try:
        from lerobot.robots.brewie.Brewie_base import CameraSubscriber
        
        # Create a dummy subscriber for testing
        subscriber = CameraSubscriber(None, None)
        decoded_image = subscriber._decode_image_from_message(mock_message)
        
        if decoded_image is not None:
            logger.info(f"✓ Base64 decoding successful: shape={decoded_image.shape}")
        else:
            logger.warning("⚠ Base64 decoding failed")
            
    except Exception as e:
        logger.error(f"Error testing image decoding: {e}")

if __name__ == "__main__":
    logger.info("Starting improved camera processing tests...")
    
    # Test image decoding first
    test_image_decoding()
    
    # Test camera processing with robot
    test_camera_processing()
    
    logger.info("All tests completed!")
