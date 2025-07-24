"""
BMM Basic Plans

Basic movement and positioning plans for BMM beamline.
Adapted from BMM/plans.py for BITS framework.
"""

import logging
import time

from bluesky.plan_stubs import mv
from bluesky.plan_stubs import mvr
from bluesky.plan_stubs import sleep
from bluesky.plans import count
from bluesky.plans import scan

logger = logging.getLogger(__name__)


def move(motor, absolute_position):
    """
    A thin wrapper around a single axis absolute move for use in queueserver.

    Parameters:
    -----------
    motor : ophyd.Device
        Motor device to move
    absolute_position : float
        Target absolute position
    """
    yield from mv(motor, absolute_position)


def mover(motor, relative_position):
    """
    A thin wrapper around a single axis relative move for use in queueserver.

    Parameters:
    -----------
    motor : ophyd.Device
        Motor device to move
    relative_position : float
        Relative position change
    """
    yield from mvr(motor, relative_position)


def multi_move(*args):
    """
    Move multiple motors to absolute positions.

    Parameters:
    -----------
    *args : alternating motor, position pairs
        motor1, position1, motor2, position2, ...
    """
    if len(args) % 2 != 0:
        raise ValueError("Arguments must be alternating motor, position pairs")

    moves = []
    for i in range(0, len(args), 2):
        moves.extend([args[i], args[i + 1]])

    yield from mv(*moves)


def multi_move_relative(*args):
    """
    Move multiple motors by relative amounts.

    Parameters:
    -----------
    *args : alternating motor, position pairs
        motor1, delta1, motor2, delta2, ...
    """
    if len(args) % 2 != 0:
        raise ValueError("Arguments must be alternating motor, position pairs")

    moves = []
    for i in range(0, len(args), 2):
        moves.extend([args[i], args[i + 1]])

    yield from mvr(*moves)


def sleep_plan(time_seconds):
    """
    Simple sleep plan.

    Parameters:
    -----------
    time_seconds : float
        Time to sleep in seconds
    """
    yield from sleep(time_seconds)


def count_plan(detectors, num=1, delay=None, md=None):
    """
    Take one or more readings from detectors.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    num : int, optional
        Number of readings, default 1
    delay : float, optional
        Delay between readings in seconds
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "count_plan",
            "detectors": [det.name for det in detectors],
            "num_points": num,
        }
    )

    yield from count(detectors, num=num, delay=delay, md=md)


def motor_scan_plan(detectors, motor, start, stop, num, md=None):
    """
    Scan a motor while collecting detector data.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    motor : ophyd.Device
        Motor to scan
    start : float
        Start position
    stop : float
        Stop position
    num : int
        Number of points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "motor_scan_plan",
            "detectors": [det.name for det in detectors],
            "motor": motor.name,
            "scan_start": start,
            "scan_stop": stop,
            "num_points": num,
        }
    )

    yield from scan(detectors, motor, start, stop, num, md=md)


def check_motor_limits(motor, target_position):
    """
    Check if target position is within motor limits.

    Parameters:
    -----------
    motor : ophyd.Device
        Motor device
    target_position : float
        Target position to check

    Returns:
    --------
    bool
        True if position is within limits
    """
    try:
        if hasattr(motor, "low_limit") and hasattr(motor, "high_limit"):
            low_limit = motor.low_limit.get()
            high_limit = motor.high_limit.get()
            return low_limit <= target_position <= high_limit
        else:
            logger.warning(f"Motor {motor.name} has no limit signals")
            return True
    except Exception as e:
        logger.warning(f"Could not check limits for {motor.name}: {e}")
        return True


def safe_move(motor, target_position):
    """
    Move motor with limit checking.

    Parameters:
    -----------
    motor : ophyd.Device
        Motor device to move
    target_position : float
        Target absolute position
    """
    if not check_motor_limits(motor, target_position):
        raise ValueError(
            f"Target position {target_position} outside limits for {motor.name}"
        )

    yield from mv(motor, target_position)


def wait_for_temperature(temp_controller, target_temp, tolerance=1.0, timeout=600):
    """
    Wait for temperature controller to stabilize.

    Parameters:
    -----------
    temp_controller : BMM temperature device
        Temperature controller
    target_temp : float
        Target temperature
    tolerance : float
        Temperature tolerance for stability
    timeout : float
        Maximum wait time in seconds
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            current_temp = temp_controller.temperature.get()
            if abs(current_temp - target_temp) < tolerance:
                logger.info(f"Temperature stable at {current_temp:.1f}")
                return
        except Exception as e:
            logger.warning(f"Could not read temperature: {e}")

        yield from sleep(5.0)

    logger.warning(f"Temperature did not stabilize within {timeout} seconds")


def motor_status_check(*motors):
    """
    Check status of multiple motors.

    Parameters:
    -----------
    *motors : ophyd.Device
        Motor devices to check

    Returns:
    --------
    dict
        Status information for each motor
    """
    status = {}
    for motor in motors:
        try:
            status[motor.name] = {
                "position": motor.position,
                "moving": motor.moving,
                "connected": motor.connected,
            }
        except Exception as e:
            status[motor.name] = {"error": str(e)}

    return status


# Convenience aliases
mv_plan = move
mvr_plan = mover
kmv = multi_move  # BMM compatibility
kmvr = multi_move_relative  # BMM compatibility
