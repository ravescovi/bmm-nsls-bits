"""
BMM XAFS Plans

X-ray Absorption Fine Structure (XAFS) measurement plans for BMM beamline.
Adapted from BMM/xafs.py and related files for BITS framework.
"""

import logging

import numpy as np
from bluesky.plan_stubs import mv
from bluesky.plan_stubs import sleep
from bluesky.plans import list_scan

logger = logging.getLogger(__name__)


def xafs_scan(detectors, energy_motor, energy_list, dwelltime_list=None, md=None):
    """
    Basic XAFS energy scan.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    energy_motor : ophyd.Device
        Energy motor (usually DCM bragg angle)
    energy_list : list or array
        List of energy points in eV
    dwelltime_list : list or array, optional
        List of dwell times per point
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    if dwelltime_list is None:
        dwelltime_list = [1.0] * len(energy_list)

    if len(energy_list) != len(dwelltime_list):
        raise ValueError("Energy list and dwelltime list must have same length")

    md.update(
        {
            "plan_name": "xafs_scan",
            "detectors": [det.name for det in detectors],
            "energy_motor": energy_motor.name,
            "energy_points": len(energy_list),
            "energy_start": min(energy_list),
            "energy_stop": max(energy_list),
        }
    )

    # Convert energies to motor positions if needed
    if hasattr(energy_motor, "energy_to_bragg"):
        position_list = [energy_motor.energy_to_bragg(e) for e in energy_list]
    else:
        position_list = energy_list

    yield from list_scan(detectors, energy_motor, position_list, md=md)


def xafs_step_scan(
    detectors,
    energy_motor,
    pre_edge_start,
    pre_edge_stop,
    pre_edge_step,
    edge_start,
    edge_stop,
    edge_step,
    post_edge_start,
    post_edge_stop,
    post_edge_step,
    md=None,
):
    """
    XAFS scan with different step sizes for pre-edge, edge, and post-edge regions.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    energy_motor : ophyd.Device
        Energy motor
    pre_edge_start, pre_edge_stop, pre_edge_step : float
        Pre-edge region parameters
    edge_start, edge_stop, edge_step : float
        Edge region parameters
    post_edge_start, post_edge_stop, post_edge_step : float
        Post-edge region parameters
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    # Build energy list
    pre_edge = np.arange(pre_edge_start, pre_edge_stop, pre_edge_step)
    edge = np.arange(edge_start, edge_stop, edge_step)
    post_edge = np.arange(post_edge_start, post_edge_stop, post_edge_step)

    energy_list = np.concatenate([pre_edge, edge, post_edge])

    md.update(
        {
            "plan_name": "xafs_step_scan",
            "pre_edge_points": len(pre_edge),
            "edge_points": len(edge),
            "post_edge_points": len(post_edge),
            "total_points": len(energy_list),
        }
    )

    yield from xafs_scan(detectors, energy_motor, energy_list, md=md)


def transmission_xafs(
    sample_name,
    energy_motor,
    i0_detector,
    it_detector,
    ir_detector=None,
    edge_energy=8000,
    scan_range=(-200, 800),
    md=None,
):
    """
    Standard transmission XAFS measurement.

    Parameters:
    -----------
    sample_name : str
        Sample identifier
    energy_motor : ophyd.Device
        Energy motor (DCM)
    i0_detector, it_detector : ophyd.Device
        I0 and It ion chambers
    ir_detector : ophyd.Device, optional
        Reference detector
    edge_energy : float
        Absorption edge energy in eV
    scan_range : tuple
        (start_offset, stop_offset) relative to edge energy
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    detectors = [i0_detector, it_detector]
    if ir_detector is not None:
        detectors.append(ir_detector)

    # Define energy regions
    start_energy = edge_energy + scan_range[0]
    stop_energy = edge_energy + scan_range[1]

    # Create energy list with appropriate step sizes
    pre_edge = np.arange(start_energy, edge_energy - 50, 5.0)
    edge = np.arange(edge_energy - 50, edge_energy + 50, 0.5)
    post_edge = np.arange(edge_energy + 50, stop_energy, 2.0)

    energy_list = np.concatenate([pre_edge, edge, post_edge])

    md.update(
        {
            "sample_name": sample_name,
            "measurement_type": "transmission_xafs",
            "edge_energy": edge_energy,
            "scan_range": scan_range,
        }
    )

    yield from xafs_scan(detectors, energy_motor, energy_list, md=md)


def fluorescence_xafs(
    sample_name,
    energy_motor,
    i0_detector,
    fluorescence_detector,
    edge_energy=8000,
    scan_range=(-200, 800),
    md=None,
):
    """
    Fluorescence XAFS measurement.

    Parameters:
    -----------
    sample_name : str
        Sample identifier
    energy_motor : ophyd.Device
        Energy motor (DCM)
    i0_detector : ophyd.Device
        I0 ion chamber
    fluorescence_detector : ophyd.Device
        Fluorescence detector (Xspress3, etc.)
    edge_energy : float
        Absorption edge energy in eV
    scan_range : tuple
        (start_offset, stop_offset) relative to edge energy
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    detectors = [i0_detector, fluorescence_detector]

    # Define energy regions
    start_energy = edge_energy + scan_range[0]
    stop_energy = edge_energy + scan_range[1]

    # Create energy list
    pre_edge = np.arange(start_energy, edge_energy - 50, 5.0)
    edge = np.arange(edge_energy - 50, edge_energy + 50, 0.5)
    post_edge = np.arange(edge_energy + 50, stop_energy, 2.0)

    energy_list = np.concatenate([pre_edge, edge, post_edge])

    md.update(
        {
            "sample_name": sample_name,
            "measurement_type": "fluorescence_xafs",
            "edge_energy": edge_energy,
            "scan_range": scan_range,
        }
    )

    yield from xafs_scan(detectors, energy_motor, energy_list, md=md)


def quick_xafs(detectors, energy_motor, edge_energy, scan_points=50, md=None):
    """
    Quick XAFS scan for alignment or testing.

    Parameters:
    -----------
    detectors : list
        List of detector devices
    energy_motor : ophyd.Device
        Energy motor
    edge_energy : float
        Absorption edge energy in eV
    scan_points : int
        Total number of scan points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    # Simple linear energy range
    start_energy = edge_energy - 100
    stop_energy = edge_energy + 200
    energy_list = np.linspace(start_energy, stop_energy, scan_points)

    md.update(
        {
            "plan_name": "quick_xafs",
            "edge_energy": edge_energy,
            "scan_points": scan_points,
        }
    )

    yield from xafs_scan(detectors, energy_motor, energy_list, md=md)


def xafs_with_temperature(
    sample_name,
    energy_motor,
    detectors,
    temp_controller,
    temperatures,
    edge_energy=8000,
    md=None,
):
    """
    XAFS measurement at multiple temperatures.

    Parameters:
    -----------
    sample_name : str
        Sample identifier
    energy_motor : ophyd.Device
        Energy motor
    detectors : list
        List of detector devices
    temp_controller : BMM temperature device
        Temperature controller
    temperatures : list
        List of temperatures for measurement
    edge_energy : float
        Absorption edge energy in eV
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    md.update(
        {
            "plan_name": "xafs_with_temperature",
            "sample_name": sample_name,
            "temperatures": temperatures,
            "edge_energy": edge_energy,
        }
    )

    # Define energy list
    pre_edge = np.arange(edge_energy - 200, edge_energy - 50, 5.0)
    edge = np.arange(edge_energy - 50, edge_energy + 50, 0.5)
    post_edge = np.arange(edge_energy + 50, edge_energy + 800, 2.0)
    energy_list = np.concatenate([pre_edge, edge, post_edge])

    for temp in temperatures:
        logger.info(f"Setting temperature to {temp}")

        # Set temperature and wait for stability
        if hasattr(temp_controller, "set_temperature"):
            yield from temp_controller.set_temperature(temp, wait=True)
        else:
            yield from mv(temp_controller.setpoint, temp)
            yield from sleep(300)  # Wait for temperature stability

        # Update metadata for this temperature
        temp_md = md.copy()
        temp_md.update({"temperature": temp, "temperature_setpoint": temp})

        # Perform XAFS scan
        yield from xafs_scan(detectors, energy_motor, energy_list, md=temp_md)


def energy_calibration_scan(
    detectors,
    energy_motor,
    reference_foil_energy,
    scan_range=(-20, 20),
    num_points=81,
    md=None,
):
    """
    Energy calibration scan using reference foil.

    Parameters:
    -----------
    detectors : list
        List of detector devices including reference detector
    energy_motor : ophyd.Device
        Energy motor
    reference_foil_energy : float
        Known edge energy of reference foil
    scan_range : tuple
        Energy range around edge for calibration
    num_points : int
        Number of scan points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}

    start_energy = reference_foil_energy + scan_range[0]
    stop_energy = reference_foil_energy + scan_range[1]
    energy_list = np.linspace(start_energy, stop_energy, num_points)

    md.update(
        {
            "plan_name": "energy_calibration_scan",
            "reference_foil_energy": reference_foil_energy,
            "scan_range": scan_range,
            "purpose": "energy_calibration",
        }
    )

    yield from xafs_scan(detectors, energy_motor, energy_list, md=md)


# Convenience functions for common elements
def copper_xafs(sample_name, detectors, energy_motor, **kwargs):
    """Copper K-edge XAFS scan."""
    return transmission_xafs(
        sample_name, energy_motor, *detectors, edge_energy=8979, **kwargs
    )


def iron_xafs(sample_name, detectors, energy_motor, **kwargs):
    """Iron K-edge XAFS scan."""
    return transmission_xafs(
        sample_name, energy_motor, *detectors, edge_energy=7112, **kwargs
    )


def zinc_xafs(sample_name, detectors, energy_motor, **kwargs):
    """Zinc K-edge XAFS scan."""
    return transmission_xafs(
        sample_name, energy_motor, *detectors, edge_energy=9659, **kwargs
    )
