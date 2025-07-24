"""
BMM Alignment Plans

Plans for beamline alignment including mirror tuning, slit optimization,
and sample positioning. Adapted from BMM plans for BITS framework.
"""

import os
import logging
import numpy as np
from bluesky.plan_stubs import sleep, mv, mvr, trigger_and_read
from bluesky.plans import scan, list_scan, count
from bluesky.preprocessors import run_decorator

logger = logging.getLogger(__name__)


def tune_dcm_pitch(pitch_motor, detector, step_size=0.004, num_steps=5, md=None):
    """
    Tune DCM second crystal pitch for maximum intensity.
    
    Parameters:
    -----------
    pitch_motor : ophyd.Device
        DCM pitch motor
    detector : ophyd.Device  
        Intensity detector (I0 or similar)
    step_size : float, optional
        Step size for tuning in degrees
    num_steps : int, optional
        Number of steps in each direction
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'tune_dcm_pitch',
        'motor': pitch_motor.name,
        'detector': detector.name,
        'step_size': step_size,
        'purpose': 'dcm_alignment'
    })
    
    # Record initial position
    initial_position = pitch_motor.position
    
    # Create scan range around current position
    start_pos = initial_position - (num_steps * step_size)
    stop_pos = initial_position + (num_steps * step_size)
    total_points = 2 * num_steps + 1
    
    logger.info(f"Tuning DCM pitch around {initial_position:.4f}")
    
    yield from scan([detector], pitch_motor, start_pos, stop_pos, total_points, md=md)
    
    # In a real implementation, would analyze results and move to peak
    logger.info("DCM pitch tuning complete - check results for optimal position")


def align_slits(slit_device, detector, scan_range=1.0, num_points=21, md=None):
    """
    Align slits for maximum throughput.
    
    Parameters:
    -----------
    slit_device : ophyd.Device
        Slit device with inboard, outboard, top, bottom motors
    detector : ophyd.Device
        Intensity detector
    scan_range : float, optional
        Range to scan each blade
    num_points : int, optional
        Number of points per scan
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'align_slits',
        'slit_device': slit_device.name,
        'detector': detector.name,
        'scan_range': scan_range,
        'purpose': 'slit_alignment'
    })
    
    # Align each blade individually
    blades = []
    if hasattr(slit_device, 'inboard'):
        blades.append(('inboard', slit_device.inboard))
    if hasattr(slit_device, 'outboard'):
        blades.append(('outboard', slit_device.outboard))
    if hasattr(slit_device, 'top'):
        blades.append(('top', slit_device.top))
    if hasattr(slit_device, 'bottom'):
        blades.append(('bottom', slit_device.bottom))
    
    for blade_name, blade_motor in blades:
        logger.info(f"Aligning {blade_name} blade")
        
        initial_pos = blade_motor.position
        start_pos = initial_pos - scan_range / 2
        stop_pos = initial_pos + scan_range / 2
        
        blade_md = md.copy()
        blade_md.update({
            'blade': blade_name,
            'blade_motor': blade_motor.name
        })
        
        yield from scan([detector], blade_motor, start_pos, stop_pos, num_points, md=blade_md)
        
        # Brief pause between blade alignments
        yield from sleep(1.0)


def mirror_alignment(mirror_device, detector, scan_motors=None, scan_range=0.1, md=None):
    """
    Align mirrors for optimal beam characteristics.
    
    Parameters:
    -----------
    mirror_device : ophyd.Device
        Mirror device with positioning motors
    detector : ophyd.Device
        Intensity or profile detector
    scan_motors : list, optional
        List of motor names to scan, defaults to ['yu', 'ydo', 'ydi']
    scan_range : float, optional
        Range to scan each motor
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    if scan_motors is None:
        scan_motors = ['yu', 'ydo', 'ydi']
    
    md.update({
        'plan_name': 'mirror_alignment',
        'mirror_device': mirror_device.name,
        'detector': detector.name,
        'scan_motors': scan_motors,
        'purpose': 'mirror_alignment'
    })
    
    for motor_name in scan_motors:
        if hasattr(mirror_device, motor_name):
            motor = getattr(mirror_device, motor_name)
            logger.info(f"Aligning mirror {motor_name}")
            
            initial_pos = motor.position
            start_pos = initial_pos - scan_range / 2
            stop_pos = initial_pos + scan_range / 2
            
            motor_md = md.copy()
            motor_md.update({
                'mirror_motor': motor_name,
                'motor_device': motor.name
            })
            
            yield from scan([detector], motor, start_pos, stop_pos, 21, md=motor_md)
            yield from sleep(1.0)
        else:
            logger.warning(f"Mirror device has no motor named {motor_name}")


def sample_height_scan(sample_motor, detector, scan_range=2.0, num_points=41, md=None):
    """
    Find optimal sample height by scanning through the beam.
    
    Parameters:
    -----------
    sample_motor : ophyd.Device
        Sample height motor (usually Y motor)
    detector : ophyd.Device
        Transmission detector (It)
    scan_range : float, optional
        Range to scan in mm
    num_points : int, optional
        Number of scan points
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'sample_height_scan',
        'motor': sample_motor.name,
        'detector': detector.name,
        'scan_range': scan_range,
        'purpose': 'sample_positioning'
    })
    
    initial_pos = sample_motor.position
    start_pos = initial_pos - scan_range / 2
    stop_pos = initial_pos + scan_range / 2
    
    logger.info(f"Scanning sample height from {start_pos:.2f} to {stop_pos:.2f}")
    
    yield from scan([detector], sample_motor, start_pos, stop_pos, num_points, md=md)


def beam_size_measurement(detector, slits, initial_size=1.0, step_size=0.1, md=None):
    """
    Measure beam size by scanning slit opening.
    
    Parameters:
    -----------
    detector : ophyd.Device
        Intensity detector
    slits : ophyd.Device
        Slit device
    initial_size : float, optional
        Initial slit opening
    step_size : float, optional
        Step size for slit opening
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'beam_size_measurement',
        'detector': detector.name,
        'slits': slits.name,
        'purpose': 'beam_characterization'
    })
    
    # Create list of slit openings
    slit_openings = np.arange(0.1, initial_size + 0.1, step_size)
    
    for opening in slit_openings:
        logger.info(f"Setting slit opening to {opening:.2f} mm")
        
        # Set slit size (simplified - assumes slits has set_size method)
        if hasattr(slits, 'set_size'):
            yield from slits.set_size(hsize=opening, vsize=opening)
        else:
            logger.warning("Slit device has no set_size method")
        
        yield from sleep(1.0)  # Allow slits to settle
        yield from count([detector], num=3, md=md)  # Take multiple readings


def find_sample_edge(sample_motor, detector, scan_range=5.0, velocity=1.0, md=None):
    """
    Find the edge of a sample by scanning across it.
    
    Parameters:
    -----------
    sample_motor : ophyd.Device
        Sample positioning motor
    detector : ophyd.Device
        Transmission detector
    scan_range : float, optional
        Range to scan
    velocity : float, optional
        Scan velocity
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'find_sample_edge',
        'motor': sample_motor.name,
        'detector': detector.name,
        'scan_range': scan_range,
        'purpose': 'edge_detection'
    })
    
    initial_pos = sample_motor.position
    start_pos = initial_pos - scan_range / 2
    stop_pos = initial_pos + scan_range / 2
    
    # Estimate number of points based on velocity
    scan_time = scan_range / velocity
    num_points = max(10, int(scan_time / 0.1))  # Assume 0.1s per point
    
    logger.info(f"Scanning for sample edge from {start_pos:.2f} to {stop_pos:.2f}")
    
    yield from scan([detector], sample_motor, start_pos, stop_pos, num_points, md=md)


def center_sample_on_beam(x_motor, y_motor, detector, scan_range=2.0, md=None):
    """
    Center sample on beam by scanning both X and Y.
    
    Parameters:
    -----------
    x_motor, y_motor : ophyd.Device
        Sample X and Y motors
    detector : ophyd.Device
        Transmission detector
    scan_range : float, optional
        Range to scan in each direction
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'center_sample_on_beam',
        'x_motor': x_motor.name,
        'y_motor': y_motor.name,
        'detector': detector.name,
        'purpose': 'sample_centering'
    })
    
    # Scan X direction first
    logger.info("Scanning X direction")
    x_initial = x_motor.position
    x_start = x_initial - scan_range / 2
    x_stop = x_initial + scan_range / 2
    
    x_md = md.copy()
    x_md.update({'scan_direction': 'X'})
    yield from scan([detector], x_motor, x_start, x_stop, 21, md=x_md)
    
    yield from sleep(2.0)
    
    # Scan Y direction
    logger.info("Scanning Y direction")
    y_initial = y_motor.position
    y_start = y_initial - scan_range / 2
    y_stop = y_initial + scan_range / 2
    
    y_md = md.copy()
    y_md.update({'scan_direction': 'Y'})
    yield from scan([detector], y_motor, y_start, y_stop, 21, md=y_md)


def energy_calibration_check(energy_motor, detector, reference_energy, md=None):
    """
    Quick energy calibration check using known reference.
    
    Parameters:
    -----------
    energy_motor : ophyd.Device
        Energy motor (DCM)
    detector : ophyd.Device
        Reference detector
    reference_energy : float
        Known reference energy in eV
    md : dict, optional
        Metadata dictionary
    """
    if md is None:
        md = {}
    
    md.update({
        'plan_name': 'energy_calibration_check',
        'energy_motor': energy_motor.name,
        'detector': detector.name,
        'reference_energy': reference_energy,
        'purpose': 'energy_calibration'
    })
    
    # Scan around reference energy
    scan_range = 20  # eV
    start_energy = reference_energy - scan_range
    stop_energy = reference_energy + scan_range
    
    logger.info(f"Checking energy calibration around {reference_energy} eV")
    
    # Convert to motor positions if needed
    if hasattr(energy_motor, 'energy_to_bragg'):
        start_pos = energy_motor.energy_to_bragg(start_energy)
        stop_pos = energy_motor.energy_to_bragg(stop_energy)
    else:
        start_pos = start_energy
        stop_pos = stop_energy
    
    yield from scan([detector], energy_motor, start_pos, stop_pos, 41, md=md)


# Convenience functions
def quick_mirror_tune(mirror, detector, motor='yu', md=None):
    """Quick mirror tuning of single motor."""
    if hasattr(mirror, motor):
        motor_obj = getattr(mirror, motor)
        return tune_dcm_pitch(motor_obj, detector, step_size=0.01, num_steps=3, md=md)
    else:
        logger.error(f"Mirror has no motor named {motor}")


def quick_slit_center(slits, detector, md=None):
    """Quick slit centering with small range."""
    return align_slits(slits, detector, scan_range=0.5, num_points=11, md=md)