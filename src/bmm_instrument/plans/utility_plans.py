"""
BMM Utility Plans

Utility and maintenance plans for BMM beamline operations.
Includes recovery procedures, diagnostics, and system checks.
"""

import logging
import time

from bluesky.plan_stubs import mv
from bluesky.plan_stubs import sleep
from bluesky.plans import count

logger = logging.getLogger(__name__)


def motor_recovery_plan(motor, safe_position=None, md=None):
    """
    Recover a motor that may be in an error state.

    Parameters:
    -----------
    motor : ophyd.Device
        Motor device to recover
    safe_position : float, optional
        Safe position to move to after recovery
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "motor_recovery_plan",
            "motor": motor.name,
            "purpose": "motor_recovery",
        }
    )

    logger.info(f"Attempting to recover motor {motor.name}")

    try:
        # Check if motor has kill command
        if hasattr(motor, "kill_cmd"):
            logger.info(f"Sending kill command to {motor.name}")
            yield from mv(motor.kill_cmd, 1)
            yield from sleep(1.0)

        # Check if motor has home command
        if hasattr(motor, "home_cmd") and hasattr(motor, "homed"):
            if not motor.homed.get():
                logger.info(f"Homing motor {motor.name}")
                yield from mv(motor.home_cmd, 1)

                # Wait for homing to complete
                timeout = 60  # seconds
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if motor.homed.get():
                        logger.info(f"Motor {motor.name} homed successfully")
                        break
                    yield from sleep(1.0)
                else:
                    logger.warning(f"Motor {motor.name} homing timed out")

        # Move to safe position if specified
        if safe_position is not None:
            logger.info(f"Moving {motor.name} to safe position {safe_position}")
            yield from mv(motor, safe_position)

        logger.info(f"Motor {motor.name} recovery complete")

    except Exception as e:
        logger.error(f"Motor recovery failed for {motor.name}: {e}")


def detector_status_check(detectors, md=None):
    """
    Check status and basic functionality of detectors.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "detector_status_check",
            "detectors": [det.name for det in detectors],
            "purpose": "detector_diagnostics",
        }
    )

    status_info = {}

    for detector in detectors:
        logger.info(f"Checking detector {detector.name}")

        try:
            # Basic connectivity check
            connected = detector.connected

            # Try to read current value
            if hasattr(detector, "get"):
                current_value = detector.get()
            else:
                current_value = None

            # Take a test measurement
            yield from count([detector], num=1, md=md)

            status_info[detector.name] = {
                "connected": connected,
                "current_value": current_value,
                "test_measurement": "successful",
            }

            logger.info(f"✓ Detector {detector.name} operational")

        except Exception as e:
            status_info[detector.name] = {
                "connected": False,
                "error": str(e),
                "test_measurement": "failed",
            }
            logger.error(f"✗ Detector {detector.name} error: {e}")

    # Store status in metadata for later retrieval
    md["detector_status"] = status_info


def beamline_status_summary(*devices, md=None):
    """
    Generate comprehensive beamline status summary.

    Parameters:
    -----------
    *devices : ophyd.Device
        Devices to check
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "beamline_status_summary",
            "devices_checked": [dev.name for dev in devices],
            "purpose": "system_diagnostics",
        }
    )

    status_summary = {}

    for device in devices:
        logger.info(f"Checking device {device.name}")

        try:
            device_status = {
                "name": device.name,
                "connected": device.connected,
                "timestamp": time.time(),
            }

            # Add device-specific information
            if hasattr(device, "position"):
                device_status["position"] = device.position

            if hasattr(device, "moving"):
                device_status["moving"] = device.moving

            if hasattr(device, "temperature") and hasattr(device.temperature, "get"):
                device_status["temperature"] = device.temperature.get()

            if hasattr(device, "is_mock"):
                device_status["mock_mode"] = device.is_mock

            status_summary[device.name] = device_status

        except Exception as e:
            status_summary[device.name] = {
                "name": device.name,
                "error": str(e),
                "connected": False,
                "timestamp": time.time(),
            }

    # Log summary
    logger.info("=== Beamline Status Summary ===")
    for device_name, status in status_summary.items():
        if "error" in status:
            logger.error(f"{device_name}: ERROR - {status['error']}")
        else:
            logger.info(f"{device_name}: Connected={status['connected']}")

    md["status_summary"] = status_summary


def energy_system_check(dcm, detectors, test_energies=None, md=None):
    """
    Check energy system functionality across energy range.

    Parameters:
    -----------
    dcm : ophyd.Device
        DCM device
    detectors : list
        List of detector devices
    test_energies : list, optional
        List of energies to test in eV
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    if test_energies is None:
        test_energies = [7000, 8000, 9000, 10000]  # Common test energies

    md.update(
        {
            "plan_name": "energy_system_check",
            "dcm": dcm.name,
            "detectors": [det.name for det in detectors],
            "test_energies": test_energies,
            "purpose": "energy_system_diagnostics",
        }
    )

    initial_energy = None
    if hasattr(dcm, "bragg") and hasattr(dcm, "bragg_to_energy"):
        try:
            initial_bragg = dcm.bragg.position
            initial_energy = dcm.bragg_to_energy(initial_bragg)
        except:
            logger.warning("Could not determine initial energy")

    energy_results = {}

    for energy in test_energies:
        logger.info(f"Testing energy system at {energy} eV")

        try:
            # Move to test energy
            if hasattr(dcm, "set_energy"):
                yield from dcm.set_energy(energy)
            elif hasattr(dcm, "energy_to_bragg"):
                bragg_angle = dcm.energy_to_bragg(energy)
                yield from mv(dcm.bragg, bragg_angle)
            else:
                logger.warning("Cannot set energy - no suitable method")
                continue

            yield from sleep(2.0)  # Allow energy to stabilize

            # Take measurement
            yield from count(detectors, num=1, md=md)

            # Check if energy was reached
            if hasattr(dcm, "bragg_to_energy"):
                current_bragg = dcm.bragg.position
                actual_energy = dcm.bragg_to_energy(current_bragg)
                energy_error = abs(actual_energy - energy)
            else:
                actual_energy = None
                energy_error = None

            energy_results[energy] = {
                "target_energy": energy,
                "actual_energy": actual_energy,
                "energy_error": energy_error,
                "success": energy_error < 1.0 if energy_error else True,
            }

            logger.info(f"✓ Energy {energy} eV test successful")

        except Exception as e:
            energy_results[energy] = {
                "target_energy": energy,
                "error": str(e),
                "success": False,
            }
            logger.error(f"✗ Energy {energy} eV test failed: {e}")

    # Return to initial energy if known
    if initial_energy is not None:
        try:
            logger.info(f"Returning to initial energy {initial_energy:.1f} eV")
            if hasattr(dcm, "set_energy"):
                yield from dcm.set_energy(initial_energy)
            else:
                initial_bragg = dcm.energy_to_bragg(initial_energy)
                yield from mv(dcm.bragg, initial_bragg)
        except Exception as e:
            logger.error(f"Could not return to initial energy: {e}")

    md["energy_test_results"] = energy_results


def temperature_system_check(temp_controllers, test_temps=None, md=None):
    """
    Check temperature control system functionality.

    Parameters:
    -----------
    temp_controllers : list
        List of temperature controller devices
    test_temps : list, optional
        List of temperatures to test
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    if test_temps is None:
        test_temps = [300, 320, 280]  # Room temp and small variations

    md.update(
        {
            "plan_name": "temperature_system_check",
            "controllers": [tc.name for tc in temp_controllers],
            "test_temperatures": test_temps,
            "purpose": "temperature_system_diagnostics",
        }
    )

    for controller in temp_controllers:
        logger.info(f"Checking temperature controller {controller.name}")

        # Store initial state
        initial_temp = None
        if hasattr(controller, "temperature"):
            try:
                initial_temp = controller.temperature.get()
            except:
                logger.warning(
                    f"Could not read initial temperature from {controller.name}"
                )

        controller_results = {}

        for test_temp in test_temps:
            logger.info(f"Testing {controller.name} at {test_temp} K")

            try:
                # Set temperature
                if hasattr(controller, "set_temperature"):
                    yield from controller.set_temperature(test_temp, wait=False)
                elif hasattr(controller, "setpoint"):
                    yield from mv(controller.setpoint, test_temp)
                else:
                    logger.warning(f"Cannot set temperature on {controller.name}")
                    continue

                yield from sleep(5.0)  # Brief wait

                # Check if setpoint was accepted
                if hasattr(controller, "setpoint"):
                    actual_setpoint = controller.setpoint.get()
                    setpoint_error = abs(actual_setpoint - test_temp)
                else:
                    actual_setpoint = None
                    setpoint_error = None

                controller_results[test_temp] = {
                    "target_temp": test_temp,
                    "actual_setpoint": actual_setpoint,
                    "setpoint_error": setpoint_error,
                    "success": setpoint_error < 1.0 if setpoint_error else True,
                }

                logger.info(f"✓ Temperature {test_temp} K setpoint test successful")

            except Exception as e:
                controller_results[test_temp] = {
                    "target_temp": test_temp,
                    "error": str(e),
                    "success": False,
                }
                logger.error(f"✗ Temperature {test_temp} K test failed: {e}")

        # Return to initial temperature if known
        if initial_temp is not None:
            try:
                logger.info(f"Returning {controller.name} to initial temperature")
                if hasattr(controller, "set_temperature"):
                    yield from controller.set_temperature(initial_temp, wait=False)
                else:
                    yield from mv(controller.setpoint, initial_temp)
            except Exception as e:
                logger.error(f"Could not return to initial temperature: {e}")

        md[f"{controller.name}_test_results"] = controller_results


def safe_shutdown_sequence(*devices, md=None):
    """
    Safe shutdown sequence for beamline devices.

    Parameters:
    -----------
    *devices : ophyd.Device
        Devices to safely shut down
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "safe_shutdown_sequence",
            "devices": [dev.name for dev in devices],
            "purpose": "safe_shutdown",
        }
    )

    logger.info("Starting safe shutdown sequence")

    # Shutdown temperature controllers first
    temp_controllers = [
        dev
        for dev in devices
        if "temp" in dev.name.lower() or "lakeshore" in dev.name.lower()
    ]
    for controller in temp_controllers:
        try:
            logger.info(f"Shutting down temperature controller {controller.name}")
            if hasattr(controller, "stop_program"):
                yield from controller.stop_program()
            yield from sleep(1.0)
        except Exception as e:
            logger.error(f"Error shutting down {controller.name}: {e}")

    # Move motors to safe positions
    motors = [
        dev for dev in devices if hasattr(dev, "position") and hasattr(dev, "move")
    ]
    for motor in motors:
        try:
            # Simple safe shutdown - could be made more sophisticated
            if hasattr(motor, "kill_cmd"):
                logger.info(f"Sending kill command to motor {motor.name}")
                yield from mv(motor.kill_cmd, 1)
            yield from sleep(0.5)
        except Exception as e:
            logger.error(f"Error shutting down motor {motor.name}: {e}")

    logger.info("Safe shutdown sequence complete")


def warm_up_sequence(*devices, md=None):
    """
    Warm-up sequence for beamline startup.

    Parameters:
    -----------
    *devices : ophyd.Device
        Devices to warm up
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "warm_up_sequence",
            "devices": [dev.name for dev in devices],
            "purpose": "startup_warmup",
        }
    )

    logger.info("Starting beamline warm-up sequence")

    # Basic connectivity checks
    for device in devices:
        try:
            logger.info(f"Checking connectivity: {device.name}")
            connected = device.connected
            if connected:
                logger.info(f"✓ {device.name} connected")
            else:
                logger.warning(f"✗ {device.name} not connected")
        except Exception as e:
            logger.error(f"Error checking {device.name}: {e}")

        yield from sleep(0.5)

    logger.info("Warm-up sequence complete")


# Convenience functions
def quick_status_check(*devices, md=None):
    """Quick connectivity check for devices."""
    return beamline_status_summary(*devices, md=md)


def emergency_stop_all_motors(*motors, md=None):
    """Emergency stop for all specified motors."""
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "emergency_stop_all_motors",
            "motors": [motor.name for motor in motors],
            "purpose": "emergency_stop",
        }
    )

    for motor in motors:
        try:
            if hasattr(motor, "kill_cmd"):
                yield from mv(motor.kill_cmd, 1)
            logger.info(f"Emergency stop sent to {motor.name}")
        except Exception as e:
            logger.error(f"Could not stop {motor.name}: {e}")


def diagnose_motor_issues(motor, md=None):
    """Comprehensive motor diagnostics."""
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "diagnose_motor_issues",
            "motor": motor.name,
            "purpose": "motor_diagnostics",
        }
    )

    logger.info(f"Diagnosing motor {motor.name}")

    diagnostics = {}

    try:
        diagnostics["connected"] = motor.connected
        diagnostics["position"] = motor.position
        diagnostics["moving"] = motor.moving

        if hasattr(motor, "low_limit"):
            diagnostics["low_limit"] = motor.low_limit.get()
        if hasattr(motor, "high_limit"):
            diagnostics["high_limit"] = motor.high_limit.get()

        if hasattr(motor, "motor_egu"):
            diagnostics["units"] = motor.motor_egu.get()

        logger.info(f"Motor diagnostics for {motor.name}: {diagnostics}")

    except Exception as e:
        logger.error(f"Motor diagnostics failed: {e}")
        diagnostics["error"] = str(e)

    md["motor_diagnostics"] = diagnostics
