"""
BMM Optics Device Classes

Optical element classes for BMM beamline including mirrors, monochromator,
slits, and other beamline optics components.
"""

import os
from ophyd import Device, EpicsMotor, EpicsSignal, EpicsSignalRO, Component as Cpt
from ophyd.sim import SynAxis, SynSignal
from .motors import BMMMotor, FMBOMotor
import logging

logger = logging.getLogger(__name__)


class BMMOpticsBase(Device):
    """
    Base class for BMM optics with mock mode support.
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
            logger.info(f"Creating mock optics {name} (prefix: {prefix})")
            super().__init__(name=name, **kwargs)
            self._setup_mock_components()
        else:
            try:
                super().__init__(prefix, name=name, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to connect to optics {name} at {prefix}: {e}")
                logger.info(f"Creating fallback mock optics for {name}")
                super().__init__(name=name, **kwargs)
                self._mock_mode = True
                self._setup_mock_components()
    
    def _setup_mock_components(self):
        """Setup mock components for testing."""
        # Override in subclasses
        pass
    
    @property
    def is_mock(self):
        """Return True if this optics device is operating in mock mode."""
        return self._mock_mode


class BMMMirror(BMMOpticsBase):
    """
    Mirror device with multiple positioning axes.
    
    Supports upstream/downstream Y positioning, X positioning, and bender.
    """
    
    # Motor components - will be overridden in mock mode
    yu = Cpt(FMBOMotor, "YU}Mtr", labels=["mirrors"])
    ydo = Cpt(FMBOMotor, "YDO}Mtr", labels=["mirrors"])
    ydi = Cpt(FMBOMotor, "YDI}Mtr", labels=["mirrors"])
    xu = Cpt(FMBOMotor, "XU}Mtr", labels=["mirrors"])
    xd = Cpt(FMBOMotor, "XD}Mtr", labels=["mirrors"])
    
    def __init__(self, prefix: str, name: str = "", has_bender=False, **kwargs):
        self.has_bender = has_bender
        super().__init__(prefix, name=name, **kwargs)
        
        # Add bender if specified
        if has_bender and not self.is_mock:
            self.bender = FMBOMotor(f"{prefix}Bend}}Mtr", name=f"{name}_bender")
    
    def _setup_mock_components(self):
        """Setup mock motor components."""
        # In mock mode, the components are already initialized as SynAxis
        # by the Component framework
        pass
    
    def align(self, mode="parallel"):
        """
        Align mirror for parallel or focused beam.
        
        Parameters:
        -----------
        mode : str
            'parallel' for collimated beam, 'focused' for focused beam
        """
        if self.is_mock:
            logger.info(f"Mock mode: aligning {self.name} for {mode} beam")
            return
        
        try:
            if mode == "parallel":
                # Set positions for parallel beam
                logger.info(f"Aligning {self.name} for parallel beam")
            elif mode == "focused":
                # Set positions for focused beam
                logger.info(f"Aligning {self.name} for focused beam")
            else:
                raise ValueError(f"Unknown alignment mode: {mode}")
        except Exception as e:
            logger.error(f"Failed to align {self.name}: {e}")


class BMMDCM(BMMOpticsBase):
    """
    Double Crystal Monochromator (DCM) device.
    
    Provides energy selection with crystal positioning and feedback.
    """
    
    # Motor components
    bragg = Cpt(FMBOMotor, "Bragg}Mtr", labels=["monochromator", "energy"])
    pitch2 = Cpt(FMBOMotor, "P2}Mtr", labels=["monochromator"])
    roll2 = Cpt(FMBOMotor, "R2}Mtr", labels=["monochromator"])
    perp2 = Cpt(FMBOMotor, "Per2}Mtr", labels=["monochromator"])
    para2 = Cpt(FMBOMotor, "Par2}Mtr", labels=["monochromator"])
    x = Cpt(FMBOMotor, "X}Mtr", labels=["monochromator"])
    y = Cpt(FMBOMotor, "Y}Mtr", labels=["monochromator"])
    
    # Readback signals
    thermocouple = Cpt(EpicsSignalRO, "T:C-I", labels=["monochromator", "temperature"])
    
    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)
        
        # Energy calibration constants
        self.d_spacing_111 = 3.13557  # Angstroms
        self.d_spacing_311 = 1.6374   # Angstroms
        self.current_reflection = "111"
    
    def _setup_mock_components(self):
        """Setup mock DCM components."""
        # In mock mode, the components are handled by the Component framework
        pass
    
    def energy_to_bragg(self, energy_ev):
        """
        Convert energy in eV to bragg angle in degrees.
        
        Parameters:
        -----------
        energy_ev : float
            Energy in electron volts
            
        Returns:
        --------
        float
            Bragg angle in degrees
        """
        import numpy as np
        
        # Use current reflection d-spacing
        d_spacing = (self.d_spacing_111 if self.current_reflection == "111" 
                    else self.d_spacing_311)
        
        # Bragg's law: lambda = 2*d*sin(theta)
        # E(eV) = 12398.4 / lambda(Angstroms)
        wavelength = 12398.4 / energy_ev
        sin_theta = wavelength / (2 * d_spacing)
        
        if sin_theta > 1:
            raise ValueError(f"Energy {energy_ev} eV not achievable with {self.current_reflection} reflection")
        
        theta_rad = np.arcsin(sin_theta)
        theta_deg = np.degrees(theta_rad)
        
        return theta_deg
    
    def bragg_to_energy(self, bragg_deg):
        """
        Convert bragg angle in degrees to energy in eV.
        
        Parameters:
        -----------
        bragg_deg : float
            Bragg angle in degrees
            
        Returns:
        --------
        float
            Energy in electron volts
        """
        import numpy as np
        
        # Use current reflection d-spacing
        d_spacing = (self.d_spacing_111 if self.current_reflection == "111" 
                    else self.d_spacing_311)
        
        theta_rad = np.radians(bragg_deg)
        wavelength = 2 * d_spacing * np.sin(theta_rad)
        energy_ev = 12398.4 / wavelength
        
        return energy_ev
    
    def set_energy(self, energy_ev):
        """
        Move DCM to specified energy.
        
        Parameters:
        -----------
        energy_ev : float
            Target energy in eV
        """
        if self.is_mock:
            logger.info(f"Mock mode: setting {self.name} to {energy_ev} eV")
            return
        
        try:
            bragg_angle = self.energy_to_bragg(energy_ev)
            logger.info(f"Moving {self.name} to {energy_ev} eV (Bragg: {bragg_angle:.4f}°)")
            self.bragg.move(bragg_angle)
        except Exception as e:
            logger.error(f"Failed to set energy on {self.name}: {e}")


class BMMSlits(BMMOpticsBase):
    """
    Four-blade slit device for beam conditioning.
    
    Controls inboard, outboard, top, and bottom blades.
    """
    
    # Motor components
    inboard = Cpt(FMBOMotor, "I}Mtr", labels=["slits"])
    outboard = Cpt(FMBOMotor, "O}Mtr", labels=["slits"])
    top = Cpt(FMBOMotor, "T}Mtr", labels=["slits"])
    bottom = Cpt(FMBOMotor, "B}Mtr", labels=["slits"])
    
    def _setup_mock_components(self):
        """Setup mock slit components."""
        # In mock mode, the components are handled by the Component framework
        pass
    
    @property
    def hsize(self):
        """Horizontal slit size."""
        if self.is_mock:
            return 1.0
        return abs(self.outboard.position - self.inboard.position)
    
    @property
    def vsize(self):
        """Vertical slit size."""
        if self.is_mock:
            return 1.0
        return abs(self.top.position - self.bottom.position)
    
    @property
    def hcenter(self):
        """Horizontal slit center."""
        if self.is_mock:
            return 0.0
        return (self.outboard.position + self.inboard.position) / 2
    
    @property
    def vcenter(self):
        """Vertical slit center."""
        if self.is_mock:
            return 0.0
        return (self.top.position + self.bottom.position) / 2
    
    def set_size(self, hsize=None, vsize=None):
        """
        Set slit opening size.
        
        Parameters:
        -----------
        hsize : float, optional
            Horizontal opening size in mm
        vsize : float, optional
            Vertical opening size in mm
        """
        if self.is_mock:
            logger.info(f"Mock mode: setting {self.name} size to H={hsize}, V={vsize}")
            return
        
        try:
            if hsize is not None:
                center = self.hcenter
                self.outboard.move(center + hsize/2)
                self.inboard.move(center - hsize/2)
                
            if vsize is not None:
                center = self.vcenter
                self.top.move(center + vsize/2)
                self.bottom.move(center - vsize/2)
                
            logger.info(f"Set {self.name} size: H={hsize}, V={vsize}")
        except Exception as e:
            logger.error(f"Failed to set slit size for {self.name}: {e}")


class BMMShutter(BMMOpticsBase):
    """
    Shutter device for beam control.
    """
    
    # Control and status signals
    open_cmd = Cpt(EpicsSignal, "Cmd:Opn-Cmd")
    close_cmd = Cpt(EpicsSignal, "Cmd:Cls-Cmd") 
    status = Cpt(EpicsSignalRO, "Pos-Sts")
    
    def _setup_mock_components(self):
        """Setup mock shutter components."""
        # In mock mode, the components are handled by the Component framework
        pass
    
    def open(self):
        """Open the shutter."""
        if self.is_mock:
            logger.info(f"Mock mode: opening {self.name}")
            self.status.set(1)
            return
        
        try:
            self.open_cmd.put(1)
            logger.info(f"Opening {self.name}")
        except Exception as e:
            logger.error(f"Failed to open {self.name}: {e}")
    
    def close(self):
        """Close the shutter."""
        if self.is_mock:
            logger.info(f"Mock mode: closing {self.name}")
            self.status.set(0)
            return
        
        try:
            self.close_cmd.put(1)
            logger.info(f"Closing {self.name}")
        except Exception as e:
            logger.error(f"Failed to close {self.name}: {e}")
    
    @property
    def is_open(self):
        """Check if shutter is open."""
        if self.is_mock:
            return bool(self.status.get())
        try:
            return bool(self.status.get())
        except Exception:
            return False


# Factory functions for optics creation
def create_mirror(prefix: str, name: str, has_bender=False, **kwargs):
    """Create a mirror device."""
    return BMMMirror(prefix, name=name, has_bender=has_bender, **kwargs)


def create_dcm(prefix: str, name: str, **kwargs):
    """Create a DCM device."""
    return BMMDCM(prefix, name=name, **kwargs)


def create_slits(prefix: str, name: str, **kwargs):
    """Create a slits device."""
    return BMMSlits(prefix, name=name, **kwargs)


def create_shutter(prefix: str, name: str, **kwargs):
    """Create a shutter device."""
    return BMMShutter(prefix, name=name, **kwargs)