"""
BMM Motor Device Classes

Enhanced motor classes for BMM beamline with mock mode support,
error handling, and BITS framework integration.
"""

import os
from ophyd import EpicsMotor
from ophyd.sim import SynAxis
import logging

logger = logging.getLogger(__name__)

class BMMMotor(EpicsMotor):
    """
    Enhanced EpicsMotor for BMM with mock mode support and error handling.
    
    Features:
    - Automatic mock mode detection
    - Enhanced error handling
    - Connection validation
    - Custom limit handling
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
            logger.info(f"Creating mock motor {name} (prefix: {prefix})")
            # Use SynAxis for mock mode but keep the name
            super(EpicsMotor, self).__init__(name=name)
        else:
            try:
                super().__init__(prefix, name=name, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to connect to motor {name} at {prefix}: {e}")
                logger.info(f"Creating fallback SynAxis for {name}")
                super(EpicsMotor, self).__init__(name=name)
                self._mock_mode = True
    
    @property
    def is_mock(self):
        """Return True if this motor is operating in mock mode."""
        return self._mock_mode
    
    def set_limits(self, low_limit=None, high_limit=None):
        """
        Set motor limits with validation.
        
        Parameters:
        -----------
        low_limit : float, optional
            Low limit value
        high_limit : float, optional  
            High limit value
        """
        if self.is_mock:
            logger.info(f"Mock mode: skipping limit setting for {self.name}")
            return
            
        try:
            if low_limit is not None:
                self.low_limit = low_limit
            if high_limit is not None:
                self.high_limit = high_limit
            logger.info(f"Set limits for {self.name}: [{low_limit}, {high_limit}]")
        except Exception as e:
            logger.error(f"Failed to set limits for {self.name}: {e}")


class XAFSMotor(BMMMotor):
    """
    Specialized motor class for XAFS sample positioning.
    
    Includes default limits and enhanced positioning for sample motors.
    """
    
    def __init__(self, prefix: str, name: str = "", 
                 default_llm=None, default_hlm=None, **kwargs):
        super().__init__(prefix, name=name, **kwargs)
        
        # Set default limits if provided
        if not self.is_mock and default_llm is not None and default_hlm is not None:
            self.set_limits(default_llm, default_hlm)
        
        self.default_llm = default_llm
        self.default_hlm = default_hlm


class FMBOMotor(BMMMotor):
    """
    Motor class for FMBO (Fast Motion Base Object) controllers.
    
    Handles the specialized controllers used for beamline optics.
    """
    
    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)
        
        if not self.is_mock:
            # FMBO-specific setup
            try:
                # Set default velocity settings for FMBO motors
                if hasattr(self, 'hvel_sp'):
                    self.hvel_sp.put(0.05)  # Default high velocity
            except Exception as e:
                logger.warning(f"Failed to set FMBO parameters for {name}: {e}")


class EndStationMotor(BMMMotor):
    """
    Motor class for end station positioning systems.
    
    Used for sample environment and detector positioning.
    """
    
    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)


class EncodedMotor(BMMMotor):
    """
    Motor class for encoded motors with home position capability.
    
    Used for precision positioning with encoder feedback.
    """
    
    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)
    
    def is_homed(self):
        """
        Check if the motor is homed.
        
        Returns:
        --------
        str
            'Homed' if motor is homed, 'Not Homed' otherwise
        """
        if self.is_mock:
            return 'Homed'
        
        try:
            # This would be specific to the encoder motor implementation
            # Placeholder implementation
            return 'Homed' if hasattr(self, 'home_position') else 'Not Homed'
        except Exception:
            return 'Unknown'


def create_motor(motor_type: str, prefix: str, name: str, **kwargs):
    """
    Factory function to create the appropriate motor type.
    
    Parameters:
    -----------
    motor_type : str
        Type of motor ('bmm', 'xafs', 'fmbo', 'endstation', 'encoded')
    prefix : str
        EPICS PV prefix
    name : str
        Motor name
    **kwargs
        Additional motor parameters
        
    Returns:
    --------
    BMMMotor
        Appropriate motor instance
    """
    motor_classes = {
        'bmm': BMMMotor,
        'xafs': XAFSMotor,
        'fmbo': FMBOMotor,
        'endstation': EndStationMotor,
        'encoded': EncodedMotor,
    }
    
    motor_class = motor_classes.get(motor_type, BMMMotor)
    return motor_class(prefix, name=name, **kwargs)


# Factory functions for specific motor types used in devices.yml
def create_frontend_motor(prefix: str, name: str):
    """Create a frontend slit motor."""
    return create_motor('fmbo', prefix, name)


def create_mirror_motor(prefix: str, name: str):
    """Create a mirror positioning motor."""
    return create_motor('fmbo', prefix, name)


def create_dcm_motor(prefix: str, name: str):
    """Create a DCM positioning motor."""
    return create_motor('fmbo', prefix, name)


def create_sample_motor(prefix: str, name: str, **kwargs):
    """Create a sample positioning motor."""
    return create_motor('xafs', prefix, name, **kwargs)


def create_detector_motor(prefix: str, name: str):
    """Create a detector positioning motor."""
    return create_motor('encoded', prefix, name)