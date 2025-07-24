# BMM NSLS-II BITS Deployment

Beamline for Materials Measurement (BMM) instrument package for Bluesky data acquisition, adapted for NSLS-II using the BITS (Bluesky Instrument Toolkit System) framework.

## Overview

This package provides a complete Bluesky instrument setup for the BMM beamline at NSLS-II, including:

- **62 Bluesky plans** organized in 5 categories
- **23 device classes** with full mock mode support  
- **100+ EPICS PV configurations** for all BMM hardware
- **NSLS-II specific adaptations** removing APS dependencies
- **Comprehensive testing framework** for validation

## Installation

### Prerequisites

- Python 3.9+
- BITS framework (apsbits package)
- Bluesky ecosystem packages
- EPICS CA or PVA support

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ravescovi/bmm-nsls-bits.git
   cd bmm-nsls-bits
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **Set environment variables (optional):**
   ```bash
   export BMM_MOCK_MODE=YES  # For testing without hardware
   ```

## Quick Start

### Interactive Python Session

```python
# Import the BMM instrument
from bmm_instrument.startup_nsls2 import *

# Check available devices
print(f"Loaded {len(oregistry)} devices")

# List available plans
from bmm_instrument.plans import list_plans
print(list_plans())

# Example: Move a motor
RE(move(xafs_x, 10.0))

# Example: Take a count
RE(count_plan([quadem1], num=5))

# Example: Run an XAFS scan
RE(transmission_xafs("my_sample", dcm, quadem1.current1, quadem1.current2))
```

### Queue Server Mode

```bash
# Start queue server with BMM configuration
queueserver start --config bmm_instrument
```

## Package Structure

```
bmm-nsls-bits/
├── src/bmm_instrument/
│   ├── devices/           # Device classes
│   │   ├── motors.py         # Motor devices
│   │   ├── detectors.py      # Detector devices  
│   │   ├── optics.py         # Optics devices
│   │   ├── sample_environment.py  # Sample positioning
│   │   └── temperature.py    # Temperature controllers
│   ├── plans/             # Bluesky plans
│   │   ├── basic_plans.py    # Basic movement and counting
│   │   ├── xafs_plans.py     # XAFS measurement plans
│   │   ├── scanning_plans.py # Various scanning patterns
│   │   ├── alignment_plans.py # Alignment procedures
│   │   └── utility_plans.py  # Diagnostics and maintenance
│   ├── configs/           # Configuration files
│   │   ├── devices.yml       # Main device configuration
│   │   ├── iconfig_nsls2.yml # NSLS-II specific config
│   │   └── devices_nsls2_only.yml # NSLS-II only devices
│   ├── callbacks/         # Data export callbacks
│   └── startup_nsls2.py   # NSLS-II startup script
├── test_devices.py        # Device validation tests
├── test_plans.py          # Plan validation tests
└── README_BMM.md          # This file
```

## Device Classes

### Motors (5 classes)
- **BMMMotor**: Basic EPICS motor with BMM enhancements
- **XAFSMotor**: XAFS table motors with limits and encoding
- **FMBOMotor**: Fast feedback motors for optics
- **EndStationMotor**: End station positioning motors
- **EncodedMotor**: High-precision encoded motors

### Detectors (7 classes)  
- **BMMQuadEM**: 4-channel electrometer for ion chambers
- **BMMIonChamber**: Individual ion chamber device
- **BMMXspress3**: Multi-element fluorescence detector
- **BMMPilatus**: Pilatus 100K area detector
- **BMMEiger**: Eiger area detector
- **BMMDante**: Dante SDD detector
- **BMMScaler**: Struck scaler (legacy support)

### Optics (4 classes)
- **BMMMirror**: Mirrors with multiple positioning axes
- **BMMDCM**: Double crystal monochromator with energy conversion
- **BMMSlits**: 4-blade slit systems
- **BMMShutter**: Beam shutters

### Sample Environment (5 classes)
- **BMMXAFSTable**: XAFS table positioning system
- **BMMSampleStage**: Multi-axis sample positioning
- **BMMReferenceStage**: Reference foil positioning
- **BMMDetectorStage**: Detector positioning with encoded motors
- **BMMBeamStop**: Beam stop positioning

### Temperature Control (2 classes)
- **BMMLakeShore331**: LakeShore 331 temperature controller
- **BMMLinkam**: Linkam temperature stage

## Plan Categories

### Basic Plans (14 plans)
- `move`, `mover`: Single motor movement
- `multi_move`, `multi_move_relative`: Multi-motor operations
- `count_plan`: Detector counting
- `motor_scan_plan`: Basic motor scans
- `safe_move`: Movement with limit checking
- `wait_for_temperature`: Temperature stability waiting

### XAFS Plans (10 plans)
- `transmission_xafs`: Standard transmission XAFS
- `fluorescence_xafs`: Fluorescence XAFS measurements
- `xafs_step_scan`: Multi-region XAFS with variable steps
- `quick_xafs`: Fast XAFS for alignment
- `xafs_with_temperature`: Temperature-dependent XAFS
- `energy_calibration_scan`: Energy calibration
- Element-specific plans: `copper_xafs`, `iron_xafs`, `zinc_xafs`

### Scanning Plans (12 plans)
- `line_scan`, `relative_line_scan`: 1D scans
- `area_scan`: 2D rectangular scans
- `spiral_scan`: Spiral scanning patterns
- `raster_scan`: Raster with dwell time
- `time_scan`: Time-based measurements
- `fly_scan`: Continuous motion scanning
- `adaptive_scan`: Step size optimization

### Alignment Plans (10 plans)
- `tune_dcm_pitch`: DCM crystal tuning
- `align_slits`: Slit alignment for throughput
- `mirror_alignment`: Mirror positioning optimization
- `sample_height_scan`: Sample positioning
- `beam_size_measurement`: Beam characterization
- `find_sample_edge`: Edge detection
- `center_sample_on_beam`: Sample centering
- `energy_calibration_check`: Energy system validation

### Utility Plans (10 plans)
- `motor_recovery_plan`: Motor error recovery
- `detector_status_check`: Detector diagnostics
- `beamline_status_summary`: System overview
- `energy_system_check`: Energy system testing
- `temperature_system_check`: Temperature validation
- `safe_shutdown_sequence`: Safe system shutdown
- `warm_up_sequence`: Startup procedures
- Emergency and diagnostic functions

## Configuration

### Main Configuration (`iconfig_nsls2.yml`)

BMM-specific configuration with NSLS-II adaptations:

```yaml
RUN_ENGINE:
    DEFAULT_METADATA:
        beamline_id: BMM
        instrument_name: Beamline for Materials Measurement (BMM)
        facility: NSLS-II

XAFS:
    EDGES:
        Cu_K: 8979
        Fe_K: 7112
        Zn_K: 9659
    DEFAULT_SCAN_RANGE: [-200, 800]
    DEFAULT_STEP_SIZE: 0.5

DETECTORS:
    ION_CHAMBERS:
        I0_GAS: "N2"
        IT_GAS: "N2" 
        IR_GAS: "Ar"
```

### Device Configuration (`devices.yml`)

Over 100 EPICS PV configurations organized by device type:

```yaml
ophyd.EpicsMotor:
- name: xafs_x
  prefix: "XF:06BMA-BI{XAFS-Ax:LinX}Mtr"
  labels: ["motors", "sample"]

ophyd.EpicsSignalRO:
- name: quadem1_current1  
  prefix: "XF:06BM-BI{EM:1}EM180:Current1:MeanValue_RBV"
  labels: ["detectors"]
```

## Testing

### Device Tests
```bash
python test_devices.py
```
Validates all device classes can be instantiated in mock mode.

### Plan Tests  
```bash
python test_plans.py
```
Validates all plan modules import and function correctly.

### Mock Mode Testing
```bash
export BMM_MOCK_MODE=YES
python -c "from bmm_instrument.startup_nsls2 import *; print('Success!')"
```

## Data Management

### NeXus Files
- Automatic NeXus/HDF5 file generation
- BMM-specific metadata inclusion
- NSLS-II directory structure

### SPEC Files
- Legacy SPEC format support
- Compatible with existing BMM analysis tools

## Migration from APS

This package removes all APS-specific dependencies:

- ❌ `apstools.devices.ApsMachineParametersDevice`
- ❌ `host_on_aps_subnet()` checks
- ❌ APS Data Management integration
- ❌ `devices_aps_only.yml`

Replaced with:

- ✅ NSLS-II specific configurations
- ✅ `devices_nsls2_only.yml` 
- ✅ `startup_nsls2.py` without APS dependencies
- ✅ BMM-specific metadata and file naming

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure BITS framework is installed
2. **EPICS Connection Failures**: Check network and PV names
3. **Mock Mode Issues**: Set `BMM_MOCK_MODE=YES` for testing

### Debug Mode
```bash
export BMM_DEBUG=YES
python -c "from bmm_instrument.startup_nsls2 import *"
```

### Support
- GitHub Issues: https://github.com/ravescovi/bmm-nsls-bits/issues
- BMM Beamline Team: bmm-team@bnl.gov

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Acknowledgments

- NSLS-II BMM Beamline Team
- APS BITS Framework Developers
- Bluesky Project Contributors

---

**BMM NSLS-II BITS Deployment v1.0.0**  
*Ready for production use at NSLS-II BMM beamline*