"""
BMM Temperature Control Device Classes

Temperature control devices for sample environment including 
LakeShore controllers, Linkam stages, and other thermal systems.
"""

import os
from ophyd import Device, EpicsSignal, EpicsSignalRO, Component as Cpt
from ophyd.sim import SynSignal
import logging
import time

logger = logging.getLogger(__name__)


class BMMTemperatureBase(Device):
    """
    Base class for BMM temperature controllers with mock mode support.
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
            logger.info(f"Creating mock temperature controller {name} (prefix: {prefix})")
            super().__init__(name=name, **kwargs)
            self._setup_mock_components()
        else:
            try:
                super().__init__(prefix, name=name, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to connect to temperature controller {name} at {prefix}: {e}")
                logger.info(f"Creating fallback mock temperature controller for {name}")
                super().__init__(name=name, **kwargs)
                self._mock_mode = True
                self._setup_mock_components()
    
    def _setup_mock_components(self):
        """Setup mock components for testing."""
        # Override in subclasses
        pass
    
    @property
    def is_mock(self):
        """Return True if this controller is operating in mock mode."""
        return self._mock_mode


class BMMLakeShore331(BMMTemperatureBase):
    """
    LakeShore 331 temperature controller for cryogenic measurements.
    
    Provides temperature control for Displex cryostat and similar systems.
    """
    
    # Temperature readbacks
    temp_a = Cpt(EpicsSignalRO, "A:T-I", labels=["temperature"])
    temp_b = Cpt(EpicsSignalRO, "B:T-I", labels=["temperature"])
    
    # Control parameters
    setpoint = Cpt(EpicsSignal, "Out1:SP", labels=["temperature", "setpoint"])
    heater_output = Cpt(EpicsSignalRO, "Out1:Pwr-I", labels=["temperature"])
    heater_range = Cpt(EpicsSignal, "Out1:Range-Sel", labels=["temperature"])
    
    # Control loop parameters
    p_gain = Cpt(EpicsSignal, "Out1:PID:P-SP", labels=["temperature", "pid"])
    i_gain = Cpt(EpicsSignal, "Out1:PID:I-SP", labels=["temperature", "pid"])
    d_gain = Cpt(EpicsSignal, "Out1:PID:D-SP", labels=["temperature", "pid"])
    
    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)
        self._target_temp = 300.0  # Room temperature default
        self._current_temp = 300.0
        self._stable_threshold = 0.5  # Kelvin
        
    def _setup_mock_components(self):
        """Setup mock LakeShore components."""
        # In mock mode, the Component framework handles mock signals automatically
        # We don't need to manually create SynSignals
        pass
    
    def set_temperature(self, target_temp, wait=False, timeout=600):
        """
        Set target temperature and optionally wait for stability.
        
        Parameters:
        -----------
        target_temp : float
            Target temperature in Kelvin
        wait : bool
            Wait for temperature to stabilize
        timeout : float
            Maximum wait time in seconds
        """
        if self.is_mock:
            logger.info(f"Mock mode: setting {self.name} to {target_temp} K")
            self.setpoint.set(target_temp)
            self.temp_a.set(target_temp)
            self.temp_b.set(target_temp)
            return
        
        try:
            self.setpoint.put(target_temp)
            self._target_temp = target_temp
            logger.info(f"Set {self.name} target temperature to {target_temp} K")
            
            if wait:
                self.wait_for_temperature(timeout=timeout)
                
        except Exception as e:
            logger.error(f"Failed to set temperature on {self.name}: {e}")
    
    def wait_for_temperature(self, timeout=600):
        """
        Wait for temperature to stabilize at setpoint.
        
        Parameters:
        -----------
        timeout : float
            Maximum wait time in seconds
        """
        if self.is_mock:
            logger.info(f"Mock mode: {self.name} temperature stable")
            return True
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                current_temp = self.temp_a.get()
                temp_error = abs(current_temp - self._target_temp)
                
                if temp_error < self._stable_threshold:
                    logger.info(f"{self.name} temperature stable at {current_temp:.1f} K")
                    return True
                
                logger.debug(f"{self.name}: {current_temp:.1f} K (target: {self._target_temp:.1f} K)")
                time.sleep(5)  # Check every 5 seconds
            
            logger.warning(f"{self.name} temperature not stable after {timeout} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for temperature on {self.name}: {e}")
            return False
    
    @property
    def temperature(self):
        """Current temperature reading from sensor A."""
        if self.is_mock:
            return self.temp_a.get()
        try:
            return self.temp_a.get()
        except Exception:
            return None
    
    @property
    def is_stable(self):
        """Check if temperature is stable at setpoint."""
        if self.is_mock:
            return True
        
        try:
            current_temp = self.temperature
            if current_temp is None:
                return False
            temp_error = abs(current_temp - self._target_temp)
            return temp_error < self._stable_threshold
        except Exception:
            return False


class BMMLinkam(BMMTemperatureBase):
    """
    Linkam T96 temperature stage controller.
    
    Provides temperature control for heating/cooling stages.
    """
    
    # Temperature signals
    temperature = Cpt(EpicsSignalRO, "T-I", labels=["temperature"])
    setpoint = Cpt(EpicsSignal, "T:SP", labels=["temperature", "setpoint"])
    
    # Control signals
    start_cmd = Cpt(EpicsSignal, "Start-Cmd", labels=["temperature"])
    stop_cmd = Cpt(EpicsSignal, "Stop-Cmd", labels=["temperature"])
    heating_rate = Cpt(EpicsSignal, "Rate:Heat-SP", labels=["temperature"])
    cooling_rate = Cpt(EpicsSignal, "Rate:Cool-SP", labels=["temperature"])
    
    # Status signals
    status = Cpt(EpicsSignalRO, "Status-Sts", labels=["temperature"])
    stage_temp = Cpt(EpicsSignalRO, "Stage:T-I", labels=["temperature"])
    
    def __init__(self, prefix: str, name: str = "", **kwargs):
        super().__init__(prefix, name=name, **kwargs)
        self._target_temp = 25.0  # Room temperature default
        self._stable_threshold = 1.0  # Celsius
        
    def _setup_mock_components(self):
        """Setup mock Linkam components."""
        # In mock mode, the Component framework handles mock signals automatically
        # We don't need to manually create SynSignals
        pass
    
    def set_temperature(self, target_temp, rate=10.0, wait=False, timeout=600):
        """
        Set target temperature with specified rate.
        
        Parameters:
        -----------
        target_temp : float
            Target temperature in Celsius
        rate : float
            Temperature change rate in C/min
        wait : bool
            Wait for temperature to stabilize
        timeout : float
            Maximum wait time in seconds
        """
        if self.is_mock:
            logger.info(f"Mock mode: setting {self.name} to {target_temp}°C at {rate}°C/min")
            self.setpoint.set(target_temp)
            self.temperature.set(target_temp)
            self.stage_temp.set(target_temp)
            return
        
        try:
            # Set heating/cooling rate
            if target_temp > self.temperature.get():
                self.heating_rate.put(rate)
            else:
                self.cooling_rate.put(rate)
            
            # Set target temperature
            self.setpoint.put(target_temp)
            self._target_temp = target_temp
            
            # Start temperature program
            self.start_cmd.put(1)
            
            logger.info(f"Set {self.name} to {target_temp}°C at {rate}°C/min")
            
            if wait:
                self.wait_for_temperature(timeout=timeout)
                
        except Exception as e:
            logger.error(f"Failed to set temperature on {self.name}: {e}")
    
    def wait_for_temperature(self, timeout=600):
        """
        Wait for temperature to stabilize at setpoint.
        
        Parameters:
        -----------
        timeout : float
            Maximum wait time in seconds
        """
        if self.is_mock:
            logger.info(f"Mock mode: {self.name} temperature stable")
            return True
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                current_temp = self.temperature.get()
                temp_error = abs(current_temp - self._target_temp)
                
                if temp_error < self._stable_threshold:
                    logger.info(f"{self.name} temperature stable at {current_temp:.1f}°C")
                    return True
                
                logger.debug(f"{self.name}: {current_temp:.1f}°C (target: {self._target_temp:.1f}°C)")
                time.sleep(10)  # Check every 10 seconds
            
            logger.warning(f"{self.name} temperature not stable after {timeout} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for temperature on {self.name}: {e}")
            return False
    
    def hold_temperature(self):
        """Hold current temperature (stop ramping)."""
        if self.is_mock:
            logger.info(f"Mock mode: holding {self.name} temperature")
            return
        
        try:
            current_temp = self.temperature.get()
            self.setpoint.put(current_temp)
            logger.info(f"Holding {self.name} at {current_temp:.1f}°C")
        except Exception as e:
            logger.error(f"Failed to hold temperature on {self.name}: {e}")
    
    def stop_program(self):
        """Stop temperature program."""
        if self.is_mock:
            logger.info(f"Mock mode: stopping {self.name} program")
            return
        
        try:
            self.stop_cmd.put(1)
            logger.info(f"Stopped {self.name} temperature program")
        except Exception as e:
            logger.error(f"Failed to stop program on {self.name}: {e}")
    
    @property
    def is_stable(self):
        """Check if temperature is stable at setpoint."""
        if self.is_mock:
            return True
        
        try:
            current_temp = self.temperature.get()
            temp_error = abs(current_temp - self._target_temp)
            return temp_error < self._stable_threshold
        except Exception:
            return False


# Factory functions for temperature controller creation
def create_lakeshore331(prefix: str, name: str, **kwargs):
    """Create a LakeShore 331 temperature controller."""
    return BMMLakeShore331(prefix, name=name, **kwargs)


def create_linkam(prefix: str, name: str, **kwargs):
    """Create a Linkam temperature stage controller."""
    return BMMLinkam(prefix, name=name, **kwargs)