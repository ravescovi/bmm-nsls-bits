"""
BMM Sample Environment Device Classes

Sample environment control devices including temperature controllers,
sample positioning stages, and environmental monitoring.
"""

import logging
import os

from ophyd import Component as Cpt
from ophyd import Device

from .motors import EncodedMotor
from .motors import EndStationMotor
from .motors import XAFSMotor

logger = logging.getLogger(__name__)


class BMMSampleEnvironmentBase(Device):
    """
    Base class for BMM sample environment with mock mode support.
    """

    def __init__(self, prefix: str, name: str = "", labels=None, **kwargs):
        # Mock mode detection
        mock_mode = (
            os.environ.get("BMM_MOCK_MODE", "NO") == "YES"
            or os.environ.get("RUNNING_IN_NSLS2_CI", "NO") == "YES"
        )

        self._labels = labels or []
        self._mock_mode = mock_mode

        if mock_mode:
            logger.info(f"Creating mock sample environment {name} (prefix: {prefix})")
            super().__init__(name=name, **kwargs)
            self._setup_mock_components()
        else:
            try:
                super().__init__(prefix, name=name, **kwargs)
            except Exception as e:
                logger.warning(
                    f"Failed to connect to sample environment {name} at {prefix}: {e}"
                )
                logger.info(f"Creating fallback mock sample environment for {name}")
                super().__init__(name=name, **kwargs)
                self._mock_mode = True
                self._setup_mock_components()

    def _setup_mock_components(self):
        """Setup mock components."""
        # In mock mode, the components are handled by the Component framework
        pass

    @property
    def is_mock(self):
        """Return True if this device is operating in mock mode."""
        return self._mock_mode


class BMMXAFSTable(BMMSampleEnvironmentBase):
    """
    XAFS table positioning system.

    Provides stable platform for sample positioning with multiple axes.
    """

    # Table positioning motors
    yu = Cpt(EndStationMotor, "YU}Mtr", labels=["xafs_table"])
    ydo = Cpt(EndStationMotor, "YDO}Mtr", labels=["xafs_table"])
    ydi = Cpt(EndStationMotor, "YDI}Mtr", labels=["xafs_table"])
    xd = Cpt(EndStationMotor, "XD}Mtr", labels=["xafs_table"])

    def _setup_mock_components(self):
        """Setup mock components."""
        # In mock mode, the components are handled by the Component framework
        pass


class BMMSampleStage(BMMSampleEnvironmentBase):
    """
    Sample positioning stage with multi-axis control.

    Provides precise sample positioning for XAFS measurements.
    """

    # Sample positioning motors
    x = Cpt(XAFSMotor, "LinX}Mtr", labels=["sample", "motors"])
    y = Cpt(XAFSMotor, "LinY}Mtr", labels=["sample", "motors"])
    rotation = Cpt(XAFSMotor, "RotS}Mtr", labels=["sample", "motors"])
    pitch = Cpt(XAFSMotor, "Roll}Mtr", labels=["sample", "motors"])  # swapped
    roll = Cpt(XAFSMotor, "Pitch}Mtr", labels=["sample", "motors"])  # swapped
    ga_rotation = Cpt(XAFSMotor, "Mtr8}Mtr", labels=["sample", "motors"])

    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)

        # Set default limits for sample positioning
        if not self.is_mock:
            self._set_default_limits()

    def _setup_mock_components(self):
        """Setup mock components."""
        # In mock mode, the components are handled by the Component framework
        pass


class BMMReferenceStage(BMMSampleEnvironmentBase):
    """
    Reference foil positioning stage.

    Controls reference materials for XAFS measurements.
    """

    # Reference positioning motors
    x = Cpt(XAFSMotor, "RefX}Mtr", labels=["reference", "motors"])
    y = Cpt(XAFSMotor, "LinXS}Mtr", labels=["reference", "motors"])
    wheel = Cpt(XAFSMotor, "Ref}Mtr", labels=["reference", "motors"])

    def _setup_mock_components(self):
        """Setup mock components."""
        # In mock mode, the components are handled by the Component framework
        pass


class BMMDetectorStage(BMMSampleEnvironmentBase):
    """
    Detector positioning stage with encoded motors.

    Precise positioning for fluorescence and transmission detectors.
    """

    # Detector positioning motors (encoded)
    x = Cpt(EncodedMotor, "Tbl_XD}Mtr", labels=["detector", "motors"])
    y = Cpt(EncodedMotor, "1}Mtr", labels=["detector", "motors"])
    z = Cpt(EncodedMotor, "2}Mtr", labels=["detector", "motors"])
    spare = Cpt(EncodedMotor, "3}Mtr", labels=["detector", "motors"])

    def _setup_mock_components(self):
        """Setup mock components."""
        # In mock mode, the components are handled by the Component framework
        pass


class BMMBeamStop(BMMSampleEnvironmentBase):
    """
    Beam stop positioning for detector protection.
    """

    # Beam stop positioning motors
    x = Cpt(EncodedMotor, "5}Mtr", labels=["beam_stop", "motors"])
    y = Cpt(EncodedMotor, "4}Mtr", labels=["beam_stop", "motors"])

    def _setup_mock_components(self):
        """Setup mock components."""
        # In mock mode, the components are handled by the Component framework
        pass


# Factory functions for sample environment creation
def create_xafs_table(prefix: str, name: str, **kwargs):
    """Create an XAFS table device."""
    return BMMXAFSTable(prefix, name=name, **kwargs)


def create_sample_stage(prefix: str, name: str, **kwargs):
    """Create a sample stage device."""
    return BMMSampleStage(prefix, name=name, **kwargs)


def create_reference_stage(prefix: str, name: str, **kwargs):
    """Create a reference stage device."""
    return BMMReferenceStage(prefix, name=name, **kwargs)


def create_detector_stage(prefix: str, name: str, **kwargs):
    """Create a detector stage device."""
    return BMMDetectorStage(prefix, name=name, **kwargs)


def create_beam_stop(prefix: str, name: str, **kwargs):
    """Create a beam stop device."""
    return BMMBeamStop(prefix, name=name, **kwargs)
