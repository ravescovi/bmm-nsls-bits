"""
BMM NSLS-II Bluesky Data Acquisition Startup

Start Bluesky Data Acquisition sessions adapted for NSLS-II BMM beamline.
Removes APS-specific dependencies and adds BMM-specific functionality.

Includes:
* Python script
* IPython console
* Jupyter notebook
* Bluesky queueserver
"""

# Standard Library Imports
import logging
import os
from pathlib import Path

from apsbits.core.best_effort_init import init_bec_peaks
from apsbits.core.catalog_init import init_catalog
from apsbits.core.instrument_init import make_devices
from apsbits.core.instrument_init import oregistry

# Core Functions
from apsbits.core.run_engine_init import init_RE

# Utility functions (non-APS specific)
from apsbits.utils.baseline_setup import setup_baseline_stream

# Configuration functions
from apsbits.utils.config_loaders import load_config
from apsbits.utils.helper_functions import register_bluesky_magics
from apsbits.utils.helper_functions import running_in_queueserver
from apsbits.utils.logging_setup import configure_logging

# BMM-specific imports
from .devices import *  # Import all BMM device classes
from .plans import *  # Import all BMM plans

# Configuration block
# Get the path to the instrument package
# Load configuration to be used by the instrument.
instrument_path = Path(__file__).parent
iconfig_path = instrument_path / "configs" / "iconfig.yml"
iconfig = load_config(iconfig_path)

# Additional logging configuration
extra_logging_configs_path = instrument_path / "configs" / "extra_logging.yml"
configure_logging(extra_logging_configs_path=extra_logging_configs_path)

logger = logging.getLogger(__name__)
logger.info("Starting BMM NSLS-II Instrument with iconfig: %s", iconfig_path)

# Discard oregistry items loaded above.
oregistry.clear()

# Command-line tools, such as %wa, %ct, ...
register_bluesky_magics()

# Bluesky initialization block
bec, peaks = init_bec_peaks(iconfig)
cat = init_catalog(iconfig)
RE, sd = init_RE(iconfig, bec_instance=bec, cat_instance=cat)

# Optional Nexus callback block
# delete this block if not using Nexus
if iconfig.get("NEXUS_DATA_FILES", {}).get("ENABLE", False):
    from .callbacks.nexus_data_file_writer import nxwriter_init

    nxwriter = nxwriter_init(RE)

# Optional SPEC callback block
# delete this block if not using SPEC
if iconfig.get("SPEC_DATA_FILES", {}).get("ENABLE", False):
    from .callbacks.spec_data_file_writer import init_specwriter_with_RE
    from .callbacks.spec_data_file_writer import newSpecFile  # noqa: F401
    from .callbacks.spec_data_file_writer import spec_comment  # noqa: F401
    from .callbacks.spec_data_file_writer import specwriter  # noqa: F401

    init_specwriter_with_RE(RE)

# Queue server block - import standard plans
if running_in_queueserver():
    # Import standard bluesky plans for queue server
    from bluesky.plans import *  # noqa: F403
else:
    # Import bluesky plans and stubs with prefixes for interactive use
    from bluesky import plan_stubs as bps  # noqa: F401
    from bluesky import plans as bp  # noqa: F401

# BMM specific device and plan loading
logger.info("Loading BMM devices from devices.yml")
RE(make_devices(clear=False, file="devices.yml"))  # Create the BMM devices

# Check if we're at NSLS-II and load NSLS-II specific devices if available
nsls2_devices_file = "devices_nsls2_only.yml"
if os.path.exists(instrument_path / "configs" / nsls2_devices_file):
    logger.info("Loading NSLS-II specific devices")
    RE(make_devices(clear=False, file=nsls2_devices_file))

# Setup baseline stream
# Devices with the label 'baseline' will be added to the baseline stream
setup_baseline_stream(sd, oregistry, connect=False)

# BMM-specific initialization
logger.info("BMM NSLS-II instrument initialization complete")

# Create convenience device references for common BMM operations
# These will be created from the devices loaded above
try:
    # Try to create common device references if they exist in oregistry
    available_devices = list(oregistry.keys())

    # Log available devices for debugging
    logger.info(f"Available devices: {len(available_devices)} devices loaded")
    logger.debug(f"Device names: {available_devices}")

    # Set mock mode status
    mock_mode = (
        os.environ.get("BMM_MOCK_MODE", "NO") == "YES"
        or os.environ.get("RUNNING_IN_NSLS2_CI", "NO") == "YES"
    )

    if mock_mode:
        logger.info("Running in MOCK MODE - no hardware connections")
    else:
        logger.info("Running in LIVE MODE - connecting to hardware")

except Exception as e:
    logger.warning(f"Could not create device references: {e}")

# Print startup summary
logger.info("=" * 50)
logger.info("BMM NSLS-II BITS Instrument Ready")
logger.info(f"Run Engine: {RE}")
logger.info(f"Best Effort Callback: {bec}")
logger.info(f"Supplemental Detectors: {sd}")
logger.info(f"Catalog: {cat}")
logger.info(f"Devices loaded: {len(oregistry)}")
logger.info(f"Mock mode: {mock_mode}")
logger.info("=" * 50)
