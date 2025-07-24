"""
BMM Ophyd-style devices.

This package provides enhanced device classes for the BMM beamline
with mock mode support, error handling, and BITS framework integration.
"""

# Motor classes
from .motors import (
    BMMMotor,
    XAFSMotor,
    FMBOMotor,
    EndStationMotor,
    EncodedMotor,
    create_motor,
    create_frontend_motor,
    create_mirror_motor,
    create_dcm_motor,
    create_sample_motor,
    create_detector_motor,
)

# Detector classes
from .detectors import (
    BMMDetectorBase,
    BMMQuadEM,
    BMMIonChamber,
    BMMXspress3,
    BMMPilatus,
    BMMEiger,
    BMMDante,
    BMMScaler,
    create_quadem,
    create_ion_chamber,
    create_xspress3,
    create_pilatus,
    create_eiger,
    create_dante,
    create_scaler,
)

# Optics classes
from .optics import (
    BMMOpticsBase,
    BMMMirror,
    BMMDCM,
    BMMSlits,
    BMMShutter,
    create_mirror,
    create_dcm,
    create_slits,
    create_shutter,
)

# Sample environment classes
from .sample_environment import (
    BMMSampleEnvironmentBase,
    BMMXAFSTable,
    BMMSampleStage,
    BMMReferenceStage,
    BMMDetectorStage,
    BMMBeamStop,
    create_xafs_table,
    create_sample_stage,
    create_reference_stage,
    create_detector_stage,
    create_beam_stop,
)

# Temperature control classes
from .temperature import (
    BMMTemperatureBase,
    BMMLakeShore331,
    BMMLinkam,
    create_lakeshore331,
    create_linkam,
)

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