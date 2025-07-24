"""
BMM Plans Package

Collection of Bluesky plans for BMM beamline operations adapted for BITS framework.
"""

# Import existing BITS plans
from .alignment_plans import *

# Import all BMM plan modules
from .basic_plans import *
from .dm_plans import dm_kickoff_workflow  # noqa: F401
from .dm_plans import dm_list_processing_jobs  # noqa: F401
from .dm_plans import dm_submit_workflow_job  # noqa: F401
from .scanning_plans import *
from .sim_plans import sim_count_plan  # noqa: F401
from .sim_plans import sim_print_plan  # noqa: F401
from .sim_plans import sim_rel_scan_plan  # noqa: F401
from .utility_plans import *
from .xafs_plans import *

# Plan categories for easy reference
BASIC_PLANS = [
    "move",
    "mover",
    "multi_move",
    "multi_move_relative",
    "sleep_plan",
    "count_plan",
    "motor_scan_plan",
    "safe_move",
    "wait_for_temperature",
    "motor_status_check",
    "mv_plan",
    "mvr_plan",
    "kmv",
    "kmvr",
]

XAFS_PLANS = [
    "xafs_scan",
    "xafs_step_scan",
    "transmission_xafs",
    "fluorescence_xafs",
    "quick_xafs",
    "xafs_with_temperature",
    "energy_calibration_scan",
    "copper_xafs",
    "iron_xafs",
    "zinc_xafs",
]

SCANNING_PLANS = [
    "line_scan",
    "relative_line_scan",
    "area_scan",
    "time_scan",
    "fly_scan",
    "spiral_scan",
    "raster_scan",
    "multi_motor_scan",
    "adaptive_scan",
    "quick_scan",
    "coarse_scan",
    "fine_scan",
]

ALIGNMENT_PLANS = [
    "tune_dcm_pitch",
    "align_slits",
    "mirror_alignment",
    "sample_height_scan",
    "beam_size_measurement",
    "find_sample_edge",
    "center_sample_on_beam",
    "energy_calibration_check",
    "quick_mirror_tune",
    "quick_slit_center",
]

UTILITY_PLANS = [
    "motor_recovery_plan",
    "detector_status_check",
    "beamline_status_summary",
    "energy_system_check",
    "temperature_system_check",
    "safe_shutdown_sequence",
    "warm_up_sequence",
    "quick_status_check",
    "emergency_stop_all_motors",
    "diagnose_motor_issues",
]

# BITS plans
BITS_PLANS = [
    "dm_kickoff_workflow",
    "dm_list_processing_jobs",
    "dm_submit_workflow_job",
    "sim_count_plan",
    "sim_print_plan",
    "sim_rel_scan_plan",
]

# All available plans
ALL_PLANS = (
    BASIC_PLANS
    + XAFS_PLANS
    + SCANNING_PLANS
    + ALIGNMENT_PLANS
    + UTILITY_PLANS
    + BITS_PLANS
)

# Plan metadata
PLAN_CATEGORIES = {
    "basic": BASIC_PLANS,
    "xafs": XAFS_PLANS,
    "scanning": SCANNING_PLANS,
    "alignment": ALIGNMENT_PLANS,
    "utility": UTILITY_PLANS,
    "bits": BITS_PLANS,
}


def list_plans(category=None):
    """
    List available plans by category.

    Parameters:
    -----------
    category : str, optional
        Plan category ('basic', 'xafs', 'scanning', 'alignment', 'utility', 'bits')
        If None, lists all categories

    Returns:
    --------
    dict or list
        Plan information
    """
    if category is None:
        return PLAN_CATEGORIES
    elif category in PLAN_CATEGORIES:
        return PLAN_CATEGORIES[category]
    else:
        raise ValueError(
            f"Unknown category: {category}. Available: {list(PLAN_CATEGORIES.keys())}"
        )


def get_plan_info(plan_name):
    """
    Get information about a specific plan.

    Parameters:
    -----------
    plan_name : str
        Name of the plan

    Returns:
    --------
    dict
        Plan information including category and module
    """
    for category, plans in PLAN_CATEGORIES.items():
        if plan_name in plans:
            return {"name": plan_name, "category": category, "available": True}

    return {"name": plan_name, "category": None, "available": False}


# Convenience function for plan discovery
def find_plans_by_keyword(keyword):
    """
    Find plans containing a keyword.

    Parameters:
    -----------
    keyword : str
        Keyword to search for

    Returns:
    --------
    list
        List of matching plan names
    """
    matching_plans = []
    keyword_lower = keyword.lower()

    for plan_name in ALL_PLANS:
        if keyword_lower in plan_name.lower():
            matching_plans.append(plan_name)

    return matching_plans


# Export version info
__version__ = "1.0.0"
__author__ = "BMM Beamline Team"
__description__ = "Bluesky plans for BMM beamline operations"
