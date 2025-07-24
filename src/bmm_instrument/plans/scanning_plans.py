"""
BMM Scanning Plans

Various scanning plans including line scans, area scans, and time scans.
Adapted from BMM/linescans.py, areascan.py, and timescan.py for BITS framework.
"""

import logging

import numpy as np
from bluesky.plan_stubs import mv
from bluesky.plan_stubs import sleep
from bluesky.plan_stubs import trigger_and_read
from bluesky.plans import count
from bluesky.plans import grid_scan
from bluesky.plans import rel_scan
from bluesky.plans import scan

logger = logging.getLogger(__name__)


def line_scan(detectors, motor, start, stop, num_points, md=None):
    """
    Basic line scan along a single motor.

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
    num_points : int
        Number of scan points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "line_scan",
            "detectors": [det.name for det in detectors],
            "motor": motor.name,
            "scan_start": start,
            "scan_stop": stop,
            "num_points": num_points,
        }
    )

    yield from scan(detectors, motor, start, stop, num_points, md=md)


def relative_line_scan(detectors, motor, start, stop, num_points, md=None):
    """
    Relative line scan (returns to original position).

    Parameters:
    -----------
    detectors : list
        List of detector devices
    motor : ophyd.Device
        Motor to scan
    start : float
        Relative start position
    stop : float
        Relative stop position
    num_points : int
        Number of scan points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "relative_line_scan",
            "detectors": [det.name for det in detectors],
            "motor": motor.name,
            "relative_start": start,
            "relative_stop": stop,
            "num_points": num_points,
        }
    )

    yield from rel_scan(detectors, motor, start, stop, num_points, md=md)


def area_scan(
    detectors,
    motor1,
    start1,
    stop1,
    num1,
    motor2,
    start2,
    stop2,
    num2,
    snake=True,
    md=None,
):
    """
    2D area scan.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    motor1 : ophyd.Device
        First motor (slow axis)
    start1, stop1 : float
        Start and stop positions for motor1
    num1 : int
        Number of points for motor1
    motor2 : ophyd.Device
        Second motor (fast axis)
    start2, stop2 : float
        Start and stop positions for motor2
    num2 : int
        Number of points for motor2
    snake : bool, optional
        Use snake scanning pattern, default True
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "area_scan",
            "detectors": [det.name for det in detectors],
            "motor1": motor1.name,
            "motor2": motor2.name,
            "scan_shape": [num1, num2],
            "total_points": num1 * num2,
            "snake_scan": snake,
        }
    )

    yield from grid_scan(
        detectors,
        motor1,
        start1,
        stop1,
        num1,
        motor2,
        start2,
        stop2,
        num2,
        snake_axes=[motor2] if snake else None,
        md=md,
    )


def time_scan(detectors, duration, interval=1.0, md=None):
    """
    Time-based measurement.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    duration : float
        Total duration in seconds
    interval : float, optional
        Time interval between measurements in seconds
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    num_points = int(duration / interval)

    md.update(
        {
            "plan_name": "time_scan",
            "detectors": [det.name for det in detectors],
            "duration": duration,
            "interval": interval,
            "num_points": num_points,
        }
    )

    for i in range(num_points):
        yield from count(detectors, num=1, md=md)
        yield from sleep(interval)


def fly_scan(detectors, motor, start, stop, velocity, md=None):
    """
    Fly scan (continuous motion while collecting data).

    Parameters:
    -----------
    detectors : list
        List of detector devices
    motor : ophyd.Device
        Motor for continuous motion
    start : float
        Start position
    stop : float
        Stop position
    velocity : float
        Scan velocity
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    distance = abs(stop - start)
    scan_time = distance / velocity

    md.update(
        {
            "plan_name": "fly_scan",
            "detectors": [det.name for det in detectors],
            "motor": motor.name,
            "scan_start": start,
            "scan_stop": stop,
            "velocity": velocity,
            "scan_time": scan_time,
        }
    )

    # This is a simplified implementation
    # Real fly scanning would require hardware-triggered collection
    logger.warning("Fly scan not fully implemented - using stepped scan")

    # Estimate number of points based on detector readout time
    estimated_points = max(10, int(scan_time / 0.1))  # Assume 0.1s readout
    yield from scan(detectors, motor, start, stop, estimated_points, md=md)


def spiral_scan(
    detectors,
    x_motor,
    y_motor,
    center_x,
    center_y,
    max_radius,
    turns=3,
    points_per_turn=50,
    md=None,
):
    """
    Spiral scan pattern.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    x_motor, y_motor : ophyd.Device
        X and Y motors
    center_x, center_y : float
        Center coordinates
    max_radius : float
        Maximum radius of spiral
    turns : int, optional
        Number of spiral turns
    points_per_turn : int, optional
        Points per turn
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    total_points = turns * points_per_turn
    angles = np.linspace(0, 2 * np.pi * turns, total_points)
    radii = np.linspace(0, max_radius, total_points)

    x_positions = center_x + radii * np.cos(angles)
    y_positions = center_y + radii * np.sin(angles)

    md.update(
        {
            "plan_name": "spiral_scan",
            "detectors": [det.name for det in detectors],
            "x_motor": x_motor.name,
            "y_motor": y_motor.name,
            "center": [center_x, center_y],
            "max_radius": max_radius,
            "turns": turns,
            "total_points": total_points,
        }
    )

    # Move to starting position
    yield from mv(x_motor, x_positions[0], y_motor, y_positions[0])

    for i, (x_pos, y_pos) in enumerate(zip(x_positions, y_positions, strict=False)):
        yield from mv(x_motor, x_pos, y_motor, y_pos)
        yield from trigger_and_read(detectors)


def raster_scan(
    detectors,
    x_motor,
    y_motor,
    x_start,
    x_stop,
    x_num,
    y_start,
    y_stop,
    y_num,
    dwell_time=1.0,
    md=None,
):
    """
    Raster scan with specified dwell time at each point.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    x_motor, y_motor : ophyd.Device
        X and Y motors
    x_start, x_stop : float
        X scan range
    x_num : int
        Number of X points
    y_start, y_stop : float
        Y scan range
    y_num : int
        Number of Y points
    dwell_time : float, optional
        Dwell time at each point in seconds
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "raster_scan",
            "detectors": [det.name for det in detectors],
            "x_motor": x_motor.name,
            "y_motor": y_motor.name,
            "scan_shape": [x_num, y_num],
            "dwell_time": dwell_time,
            "total_points": x_num * y_num,
        }
    )

    x_positions = np.linspace(x_start, x_stop, x_num)
    y_positions = np.linspace(y_start, y_stop, y_num)

    for i, y_pos in enumerate(y_positions):
        yield from mv(y_motor, y_pos)

        # Snake pattern - reverse direction on odd rows
        if i % 2 == 1:
            x_scan_positions = x_positions[::-1]
        else:
            x_scan_positions = x_positions

        for x_pos in x_scan_positions:
            yield from mv(x_motor, x_pos)
            yield from sleep(dwell_time)
            yield from trigger_and_read(detectors)


def multi_motor_scan(detectors, motors_and_ranges, num_points, md=None):
    """
    Scan multiple motors simultaneously.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    motors_and_ranges : list of tuples
        [(motor1, start1, stop1), (motor2, start2, stop2), ...]
    num_points : int
        Number of scan points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    if len(motors_and_ranges) == 0:
        raise ValueError("Must specify at least one motor")

    # Build scan arguments
    scan_args = []
    motor_info = {}

    for motor, start, stop in motors_and_ranges:
        scan_args.extend([motor, start, stop])
        motor_info[motor.name] = {"start": start, "stop": stop}

    scan_args.append(num_points)

    md.update(
        {
            "plan_name": "multi_motor_scan",
            "detectors": [det.name for det in detectors],
            "motors": motor_info,
            "num_points": num_points,
        }
    )

    yield from scan(detectors, *scan_args, md=md)


def adaptive_scan(
    detectors,
    motor,
    start,
    stop,
    target_delta=0.05,
    min_step=0.01,
    max_step=1.0,
    md=None,
):
    """
    Adaptive scan that adjusts step size based on signal changes.

    Parameters:
    -----------
    detectors : list
        List of detector devices (first detector used for adaptation)
    motor : ophyd.Device
        Motor to scan
    start : float
        Start position
    stop : float
        Stop position
    target_delta : float, optional
        Target signal change for step adjustment
    min_step : float, optional
        Minimum step size
    max_step : float, optional
        Maximum step size
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "adaptive_scan",
            "detectors": [det.name for det in detectors],
            "motor": motor.name,
            "scan_start": start,
            "scan_stop": stop,
            "target_delta": target_delta,
        }
    )

    # Simplified adaptive scanning - in practice would need more sophisticated logic
    logger.warning("Adaptive scan using simplified implementation")

    current_pos = start
    step_size = min(max_step, (stop - start) / 10)  # Initial step

    yield from mv(motor, current_pos)

    while current_pos < stop:
        yield from trigger_and_read(detectors)

        next_pos = min(current_pos + step_size, stop)
        yield from mv(motor, next_pos)
        current_pos = next_pos

        # In real implementation, would analyze signal change and adjust step_size


# Convenience functions
def quick_scan(detectors, motor, center, range_size, num_points=21, md=None):
    """Quick scan around a center position."""
    start = center - range_size / 2
    stop = center + range_size / 2
    return line_scan(detectors, motor, start, stop, num_points, md=md)


def coarse_scan(detectors, motor, start, stop, num_points=11, md=None):
    """Coarse scan for rough positioning."""
    return line_scan(detectors, motor, start, stop, num_points, md=md)


def fine_scan(detectors, motor, start, stop, num_points=51, md=None):
    """Fine scan for precise positioning."""
    return line_scan(detectors, motor, start, stop, num_points, md=md)
