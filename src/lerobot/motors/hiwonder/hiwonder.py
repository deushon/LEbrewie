#!/usr/bin/env python

# Minimal Hiwonder motors bus adapter wrapping ros_robot_controller_sdk.Board

from __future__ import annotations

import time
from copy import deepcopy
from typing import Any

from ..motors_bus import MotorsBus
from ..motors_bus import Motor, MotorCalibration


class HiwonderMotorsBus(MotorsBus):
    """
    Minimal MotorsBus implementation for Hiwonder HX series via Hiwonder controller.

    Assumptions:
    - Position units are pulses in [0, 1000].
    - We provide only Present_Position and Goal_Position.
    - Torque enable/disable is supported.
    - Port defaults to "/dev/rrc" per SDK; Windows users should pass COMx.
    """

    # Simplified capability tables for normalization in base class
    available_baudrates = [1_000_000]
    default_timeout = 1000
    # For this adapter, we expose only minimal normalized items
    model_baudrate_table = {"hx": {"baudrates": available_baudrates}}
    model_ctrl_table = {
        "hx": {
            "Present_Position": {"address": 0, "length": 2},
            "Goal_Position": {"address": 0, "length": 2},
            "Operating_Mode": {"address": 0, "length": 1},
            "P_Coefficient": {"address": 0, "length": 1},
            "I_Coefficient": {"address": 0, "length": 1},
            "D_Coefficient": {"address": 0, "length": 1},
            "Max_Torque_Limit": {"address": 0, "length": 2},
            "Protection_Current": {"address": 0, "length": 2},
            "Overload_Torque": {"address": 0, "length": 1},
        }
    }
    # Raw is pulses 0..1000
    model_encoding_table = {"hx": {"sign": {"Present_Position": 1, "Goal_Position": 1}}}
    model_number_table = {"hx": 0}
    model_resolution_table = {"hx": {"Present_Position": 1, "Goal_Position": 1}}
    normalized_data = ["Present_Position", "Goal_Position"]

    def __init__(
        self,
        port: str,
        motors: dict[str, Motor],
        calibration: dict[str, MotorCalibration] | None = None,
    ):
        super().__init__(port, motors, calibration)
        # Lazy import to avoid hard dependency when unused
        from lerobot.robots.brewie.timor_DATA.ros_robot_controller_sdk import Board

        self._Board = Board
        self.board = None
        self._connected = False

    # Protocol checks are not applicable for this adapter
    def _assert_protocol_is_compatible(self, instruction_name: str) -> None:
        return

    def _handshake(self) -> None:
        # Hiwonder bus requires no broadcast ping; assume presence
        return

    def _find_single_motor(self, motor: str, initial_baudrate: int | None = None) -> tuple[int, int]:
        # Return (id, baud) based on configured Motor
        md = self.motors[motor]
        return md.id, self.available_baudrates[0]

    def configure_motors(self) -> None:
        # Configure motors with Hiwonder-specific settings
        if not self.board:
            return
        for motor_name, motor in self.motors.items():
            # Enable torque for all motors
            self.board.bus_servo_enable_torque(motor.id, 1)
            # Set basic parameters if needed
            # Note: Hiwonder servos may not support all these parameters
            # This is a simplified configuration

    def disable_torque(self, motors: int | str | list[str] | None = None, num_retry: int = 0) -> None:
        if not self.board:
            return
        for motor_name in self._get_motors_list(motors):
            self._disable_torque(self.motors[motor_name].id, self.motors[motor_name].model, num_retry)

    def _disable_torque(self, motor: int, model: str, num_retry: int = 0) -> None:
        # Hiwonder uses enable_torque(servo_id, enable), 0 to disable torque
        self.board.bus_servo_enable_torque(motor, 0)

    def enable_torque(self, motors: str | list[str] | None = None, num_retry: int = 0) -> None:
        if not self.board:
            return
        for motor_name in self._get_motors_list(motors):
            self.board.bus_servo_enable_torque(self.motors[motor_name].id, 1)

    # Connection management
    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        if self._connected:
            return
        self.board = self._Board(device=self.port, baudrate=1_000_000, timeout=int(self.default_timeout / 1000))
        # For reading reports if needed; positions are polled, so not strictly required
        self.board.enable_reception(True)
        time.sleep(0.05)
        self._connected = True

    def disconnect(self, disable_torque: bool = True) -> None:
        if not self._connected:
            return
        if disable_torque:
            self.disable_torque()
        # Stop reception and close serial internally when GC
        self.board.enable_reception(False)
        self.board = None
        self._connected = False

    # Calibration passthrough
    def is_calibrated(self) -> bool:
        return self.calibration is not None and len(self.calibration) > 0

    def read_calibration(self) -> dict[str, MotorCalibration] | None:
        return deepcopy(self.calibration)

    def write_calibration(self, calibration_dict: dict[str, MotorCalibration]) -> None:
        self.calibration = deepcopy(calibration_dict)

    # Sync operations (only Present_Position and Goal_Position)
    def sync_read(self, data_name: str, motors: list[str] | None = None, normalize: bool = True) -> dict[str, Any]:
        assert data_name in ("Present_Position",), f"Unsupported read: {data_name}"
        result: dict[str, Any] = {}
        for motor_name in motors or list(self.motors.keys()):
            sid = self.motors[motor_name].id
            data = self.board.bus_servo_read_position(sid)
            # SDK returns tuple or list where first element is position
            if isinstance(data, (list, tuple)):
                raw = int(data[0])
            else:
                raw = int(data) if data is not None else 0
            result[motor_name] = self._decode("Present_Position", self.motors[motor_name], raw) if normalize else raw
        return result

    def sync_write(self, data_name: str, motors_values: dict[str, Any], normalize: bool = True) -> None:
        if data_name == "Goal_Position":
            # Hiwonder groups positions as [[id, pulse], ...] with duration in seconds
            positions = []
            for motor_name, value in motors_values.items():
                raw = self._encode("Goal_Position", self.motors[motor_name], value) if normalize else int(value)
                positions.append([self.motors[motor_name].id, int(raw)])
            # Use a small duration for smoothness
            self.board.bus_servo_set_position(0.05, positions)
        else:
            # For other fields (Operating_Mode, P_Coefficient, etc.), we don't support them in Hiwonder
            # Just log a warning and continue
            print(f"Warning: {data_name} not supported for Hiwonder servos, skipping...")

    def write(self, data_name: str, motor: str, value: Any, normalize: bool = True) -> None:
        """Write a single value to a single motor."""
        self.sync_write(data_name, {motor: value}, normalize)

    def read(self, data_name: str, motor: str, normalize: bool = True) -> Any:
        """Read a single value from a single motor."""
        result = self.sync_read(data_name, [motor], normalize)
        return result[motor] if motor in result else None

    # Encoding/decoding: map normalized degrees or [-100,100] to pulses [0,1000]
    def _encode(self, data_name: str, motor: Motor, value: float) -> int:
        # If degrees mode, assume 0..240 deg mapped to 0..1000
        if motor.norm_mode.name == "DEGREES":
            # Centered mapping if calibration homing_offset provided
            return int(max(0, min(1000, round(value * (1000.0 / 240.0)))))
        elif motor.norm_mode.name in ("RANGE_M100_100", "RANGE_0_100"):
            # Map [-100,100] -> [0,1000] or [0,100]->[0,1000]
            if motor.norm_mode.name == "RANGE_M100_100":
                v = max(-100.0, min(100.0, float(value)))
                return int(round((v + 100.0) * 5.0))
            else:
                v = max(0.0, min(100.0, float(value)))
                return int(round(v * 10.0))
        return int(value)

    def _decode(self, data_name: str, motor: Motor, raw: int) -> float:
        if motor.norm_mode.name == "DEGREES":
            return float(raw) * (240.0 / 1000.0)
        elif motor.norm_mode.name == "RANGE_M100_100":
            return (float(raw) / 5.0) - 100.0
        elif motor.norm_mode.name == "RANGE_0_100":
            return float(raw) / 10.0
        return float(raw)

    # Required abstract methods from MotorsBus
    def _decode_sign(self, data_name: str, ids_values: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Decode sign for Hiwonder motors - not applicable for this implementation."""
        return ids_values

    def _encode_sign(self, data_name: str, ids_values: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Encode sign for Hiwonder motors - not applicable for this implementation."""
        return ids_values

    def _get_half_turn_homings(self, positions: dict[str, int]) -> dict[str, int]:
        """Get half turn homing positions for calibration."""
        # For Hiwonder, assume center position is 500 (middle of 0-1000 range)
        return {motor: 500 for motor in positions.keys()}

    def _split_into_byte_chunks(self, value: int, length: int) -> list[int]:
        """Split value into byte chunks - not used in Hiwonder implementation."""
        return [value & 0xFF, (value >> 8) & 0xFF][:length]

    def broadcast_ping(self, num_retry: int = 0, raise_on_error: bool = True) -> dict[str, tuple[int, int]]:
        """Broadcast ping to find motors - simplified for Hiwonder."""
        result = {}
        for motor_name, motor in self.motors.items():
            try:
                # Try to read position to verify motor exists
                data = self.board.bus_servo_read_position(motor.id)
                if data is not None:
                    result[motor_name] = (motor.id, self.available_baudrates[0])
            except Exception:
                if raise_on_error:
                    raise
        return result


