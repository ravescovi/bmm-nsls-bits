"""
BMM Ophyd-style devices.

This package provides enhanced device classes for the BMM beamline
with mock mode support, error handling, and BITS framework integration.
"""

# Motor classes
from .detectors import BMMDante

# Detector classes
from .detectors import BMMDetectorBase
from .detectors import BMMEiger
from .detectors import BMMIonChamber
from .detectors import BMMPilatus
from .detectors import BMMQuadEM
from .detectors import BMMScaler
from .detectors import BMMXspress3
from .detectors import create_dante
from .detectors import create_eiger
from .detectors import create_ion_chamber
from .detectors import create_pilatus
from .detectors import create_quadem
from .detectors import create_scaler
from .detectors import create_xspress3
from .motors import BMMMotor
from .motors import EncodedMotor
from .motors import EndStationMotor
from .motors import FMBOMotor
from .motors import XAFSMotor
from .motors import create_dcm_motor
from .motors import create_detector_motor
from .motors import create_frontend_motor
from .motors import create_mirror_motor
from .motors import create_motor
from .motors import create_sample_motor
from .optics import BMMDCM
from .optics import BMMMirror

# Optics classes
from .optics import BMMOpticsBase
from .optics import BMMShutter
from .optics import BMMSlits
from .optics import create_dcm
from .optics import create_mirror
from .optics import create_shutter
from .optics import create_slits
from .sample_environment import BMMBeamStop
from .sample_environment import BMMDetectorStage
from .sample_environment import BMMReferenceStage

# Sample environment classes
from .sample_environment import BMMSampleEnvironmentBase
from .sample_environment import BMMSampleStage
from .sample_environment import BMMXAFSTable
from .sample_environment import create_beam_stop
from .sample_environment import create_detector_stage
from .sample_environment import create_reference_stage
from .sample_environment import create_sample_stage
from .sample_environment import create_xafs_table
from .temperature import BMMLakeShore331
from .temperature import BMMLinkam

# Temperature control classes
from .temperature import BMMTemperatureBase
from .temperature import create_lakeshore331
from .temperature import create_linkam

__all__ = [
    # Motor classes
    "BMMMotor",
    "XAFSMotor",
    "FMBOMotor",
    "EndStationMotor",
    "EncodedMotor",
    "create_motor",
    "create_frontend_motor",
    "create_mirror_motor",
    "create_dcm_motor",
    "create_sample_motor",
    "create_detector_motor",
    # Detector classes
    "BMMDetectorBase",
    "BMMQuadEM",
    "BMMIonChamber",
    "BMMXspress3",
    "BMMPilatus",
    "BMMEiger",
    "BMMDante",
    "BMMScaler",
    "create_quadem",
    "create_ion_chamber",
    "create_xspress3",
    "create_pilatus",
    "create_eiger",
    "create_dante",
    "create_scaler",
    # Optics classes
    "BMMOpticsBase",
    "BMMMirror",
    "BMMDCM",
    "BMMSlits",
    "BMMShutter",
    "create_mirror",
    "create_dcm",
    "create_slits",
    "create_shutter",
    # Sample environment classes
    "BMMSampleEnvironmentBase",
    "BMMXAFSTable",
    "BMMSampleStage",
    "BMMReferenceStage",
    "BMMDetectorStage",
    "BMMBeamStop",
    "create_xafs_table",
    "create_sample_stage",
    "create_reference_stage",
    "create_detector_stage",
    "create_beam_stop",
    # Temperature control classes
    "BMMTemperatureBase",
    "BMMLakeShore331",
    "BMMLinkam",
    "create_lakeshore331",
    "create_linkam",
]
